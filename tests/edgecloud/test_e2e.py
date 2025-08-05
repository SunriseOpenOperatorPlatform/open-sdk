# -*- coding: utf-8 -*-
##
# This file is part of the Open SDK
#
# Contributors:
#   - Adrián Pino Martínez (adrian.pino@i2cat.net)
#   - Sergio Giménez (sergio.gimenez@i2cat.net)
##
"""
EdgeCloud adapters Integration Tests

Validates the complete application lifecycle:
1. Infrastructure (zone discovery)
2. Artefact management (create/delete)
3. Application lifecycle (onboard/deploy/undeploy/delete app onboarded)

Key features:
- Tests all client implementations (parametrized via test_cases)
- Tests configuration available in test_config.py
- Ensures proper resource cleanup
- Uses shared test constants and CAMARA-compliant manifests
- Includes artefact unit tests where needed
"""
import time

import pytest
from requests import Response

from sunrise6g_opensdk.common.sdk import Sdk as sdkclient
from sunrise6g_opensdk.edgecloud.adapters.errors import EdgeCloudPlatformError
from sunrise6g_opensdk.edgecloud.adapters.i2edge.client import (
    EdgeApplicationManager as I2EdgeClient,
)
from sunrise6g_opensdk.edgecloud.adapters.kubernetes.client import (
    EdgeApplicationManager as KubernetesClient,
)
from sunrise6g_opensdk.edgecloud.core import schemas as camara_schemas
from tests.edgecloud.test_cases import test_cases
from tests.edgecloud.test_config import CONFIG


@pytest.fixture(scope="module", name="edgecloud_client")
def instantiate_edgecloud_client(request):
    """Fixture to create and share an edgecloud client across tests"""
    adapter_specs = request.param
    client_name = adapter_specs["edgecloud"]["client_name"]
    adapters = sdkclient.create_adapters_from(adapter_specs)
    client = adapters.get("edgecloud")
    client.client_name = client_name
    return client


def id_func(val):
    return val["edgecloud"]["client_name"]


@pytest.mark.parametrize("edgecloud_client", test_cases, ids=id_func, indirect=True)
def test_config_camara_compliance(edgecloud_client):
    """Validate that all test configurations are CAMARA-compliant"""
    config = CONFIG[edgecloud_client.client_name]

    try:
        # Validate APP_ONBOARD_MANIFEST is CAMARA-compliant
        if "APP_ONBOARD_MANIFEST" in config:
            app_manifest = config["APP_ONBOARD_MANIFEST"]
            camara_schemas.AppManifest(**app_manifest)

        # Validate APP_DEPLOY_PAYLOAD is CAMARA-compliant
        if "APP_DEPLOY_PAYLOAD" in config:
            deploy_payload = config["APP_DEPLOY_PAYLOAD"]

            # Validate appId
            assert "appId" in deploy_payload
            camara_schemas.AppId(root=deploy_payload["appId"])

            # Validate appZones structure
            assert "appZones" in deploy_payload
            assert isinstance(deploy_payload["appZones"], list)
            assert len(deploy_payload["appZones"]) > 0

            for zone_data in deploy_payload["appZones"]:
                assert "EdgeCloudZone" in zone_data
                edge_cloud_zone = zone_data["EdgeCloudZone"]
                camara_schemas.EdgeCloudZone(
                    **edge_cloud_zone
                )  # Validate against CAMARA EdgeCloudZone schema

        # Validate APP_ID is consistent
        if "APP_ID" in config:
            app_id = config["APP_ID"]
            camara_schemas.AppId(root=app_id)

            # Check consistency between APP_ID and manifest/payload
            if "APP_ONBOARD_MANIFEST" in config:
                assert config["APP_ONBOARD_MANIFEST"]["appId"] == app_id
            if "APP_DEPLOY_PAYLOAD" in config:
                assert config["APP_DEPLOY_PAYLOAD"]["appId"] == app_id

    except Exception as e:
        pytest.fail(
            f"Configuration is not CAMARA-compliant for {edgecloud_client.client_name}: {e}"
        )


@pytest.mark.parametrize("edgecloud_client", test_cases, ids=id_func, indirect=True)
def test_get_edge_cloud_zones(edgecloud_client):
    config = CONFIG[edgecloud_client.client_name]
    try:
        response = edgecloud_client.get_edge_cloud_zones()
        assert isinstance(response, Response)
        assert response.status_code == 200
        zones = response.json()
        assert isinstance(zones, list)

        # CAMARA schema validation for each zone
        validated_zones = []
        for zone in zones:
            validated_zone = camara_schemas.EdgeCloudZone(**zone)
            validated_zones.append(validated_zone)

        # Logical validation: verify our expected zone is in the list
        expected_zone_id = config["ZONE_ID"]
        found_expected_zone = any(
            str(zone.edgeCloudZoneId.root) == expected_zone_id for zone in validated_zones
        )
        assert found_expected_zone, f"Expected zone {expected_zone_id} not found in returned zones"

    except EdgeCloudPlatformError as e:
        pytest.fail(f"Failed to retrieve zones: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error during zone validation: {e}")


@pytest.mark.parametrize("edgecloud_client", test_cases, ids=id_func, indirect=True)
def test_create_artefact(edgecloud_client):
    config = CONFIG[edgecloud_client.client_name]
    if isinstance(edgecloud_client, I2EdgeClient):
        try:
            edgecloud_client.create_artefact(
                artefact_id=config["ARTEFACT_ID"],
                artefact_name=config["ARTEFACT_NAME"],
                repo_name=config["REPO_NAME"],
                repo_type=config["REPO_TYPE"],
                repo_url=config["REPO_URL"],
                password=None,
                token=None,
                user_name=None,
            )
        except EdgeCloudPlatformError as e:
            pytest.fail(f"Artefact creation failed: {e}")


@pytest.mark.parametrize("edgecloud_client", test_cases, ids=id_func, indirect=True)
def test_onboard_app(edgecloud_client):
    config = CONFIG[edgecloud_client.client_name]
    try:
        response = edgecloud_client.onboard_app(config["APP_ONBOARD_MANIFEST"])
        assert isinstance(response, Response)
        assert response.status_code == 201

        payload = response.json()
        assert isinstance(payload, dict)

        # Use CAMARA schema validation for submitted app response
        submitted_app = camara_schemas.SubmittedApp(**payload)
        assert submitted_app.appId.root == config["APP_ID"]

    except EdgeCloudPlatformError as e:
        pytest.fail(f"App onboarding failed: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error during app onboarding: {e}")


@pytest.fixture(scope="module")
def app_instance_id(edgecloud_client):
    config = CONFIG[edgecloud_client.client_name]
    try:
        # Use standardized CAMARA structure for all adapters
        deploy_payload = config["APP_DEPLOY_PAYLOAD"]
        app_id = deploy_payload["appId"]
        app_zones = deploy_payload["appZones"]

        # edgecloud_client.deploy_app maps with CAMARA POST /appinstances
        response = edgecloud_client.deploy_app(app_id, app_zones)

        assert isinstance(response, Response)
        assert (
            response.status_code == 202
        ), f"Expected 202, got {response.status_code}: {response.text}"

        response_data = response.json()
        instance_info = camara_schemas.AppInstanceInfo(**response_data)

        # Extract appInstanceId from the validated object
        app_instance_id = instance_info.appInstanceId.root

        assert app_instance_id is not None
        yield app_instance_id
    finally:
        pass


@pytest.mark.parametrize("edgecloud_client", test_cases, ids=id_func, indirect=True)
def test_deploy_app(app_instance_id):
    assert app_instance_id is not None


@pytest.mark.parametrize("edgecloud_client", test_cases, ids=id_func, indirect=True)
def test_timer_wait_30_seconds(edgecloud_client):
    time.sleep(30)


@pytest.mark.parametrize("edgecloud_client", test_cases, ids=id_func, indirect=True)
def test_get_onboarded_app(edgecloud_client):
    """Test retrieving a specific onboarded application"""
    config = CONFIG[edgecloud_client.client_name]
    try:
        app_id = config["APP_ID"]
        response = edgecloud_client.get_onboarded_app(app_id)
        assert isinstance(response, Response)
        assert response.status_code == 200

        app_data = response.json()
        assert isinstance(app_data, dict)
        assert "appManifest" in app_data

        # Use CAMARA schema validation instead of manual checks
        app_manifest = camara_schemas.AppManifest(**app_data["appManifest"])
        assert app_manifest.appId.root == app_id

    except EdgeCloudPlatformError as e:
        pytest.fail(f"Failed to get onboarded app: {e}")


@pytest.mark.parametrize("edgecloud_client", test_cases, ids=id_func, indirect=True)
def test_get_all_onboarded_apps(edgecloud_client):
    """Test retrieving all onboarded applications"""
    config = CONFIG[edgecloud_client.client_name]
    try:
        response = edgecloud_client.get_all_onboarded_apps()
        assert isinstance(response, Response)
        assert response.status_code == 200

        apps_data = response.json()
        assert isinstance(apps_data, list)

        # CAMARA schema validation for each app manifest

        # K8s adapter uses a db with other items, irrelevant to SUNRISE6G, so this is filtering out the irrelevant ones
        if isinstance(edgecloud_client, KubernetesClient):
            apps_data = filter(lambda d: d["appId"] == config["APP_ID"], apps_data)

        validated_apps = []
        for app_manifest_data in apps_data:
            validated_app = camara_schemas.AppManifest(**app_manifest_data)
            validated_apps.append(validated_app)

        # Logical validation: verify our onboarded app is in the list
        expected_app_id = config["APP_ID"]
        found_expected_app = any(str(app.appId.root) == expected_app_id for app in validated_apps)
        assert found_expected_app, f"Expected app {expected_app_id} not found in onboarded apps"

    except EdgeCloudPlatformError as e:
        pytest.fail(f"Failed to get all onboarded apps: {e}")


@pytest.mark.parametrize("edgecloud_client", test_cases, ids=id_func, indirect=True)
def test_get_all_deployed_apps(edgecloud_client):
    """Test retrieving all deployed application instances"""
    try:
        response = edgecloud_client.get_all_deployed_apps()
        assert isinstance(response, Response)
        assert response.status_code == 200

        instances_data = response.json()
        assert isinstance(instances_data, dict)
        assert "appInstances" in instances_data
        assert isinstance(instances_data["appInstances"], list)

        # CAMARA schema validation for each app instance
        validated_instances = []
        for instance_data in instances_data["appInstances"]:
            validated_instance = camara_schemas.AppInstanceInfo(**instance_data)
            validated_instances.append(validated_instance)

        # TODO: validate that the newly created app instance is in the list

    except EdgeCloudPlatformError as e:
        pytest.fail(f"Failed to get all deployed apps: {e}")


@pytest.mark.parametrize("edgecloud_client", test_cases, ids=id_func, indirect=True)
def test_get_deployed_app(edgecloud_client, app_instance_id):
    """Test retrieving a specific deployed application instance"""
    try:
        response = edgecloud_client.get_deployed_app(app_instance_id)
        assert isinstance(response, Response)
        assert response.status_code == 200

        instance_data = response.json()
        assert isinstance(instance_data, dict)
        assert "appInstance" in instance_data

        # Use CAMARA schema validation for the app instance
        app_instance = camara_schemas.AppInstanceInfo(**instance_data["appInstance"])
        assert app_instance.appInstanceId.root == app_instance_id

        # TODO: validate that we can get the newly created app

    except EdgeCloudPlatformError as e:
        pytest.fail(f"Failed to get deployed app: {e}")


@pytest.mark.parametrize("edgecloud_client", test_cases, ids=id_func, indirect=True)
def test_undeploy_app(edgecloud_client, app_instance_id):
    try:
        response = edgecloud_client.undeploy_app(app_instance_id)
        assert isinstance(response, Response)
        assert response.status_code == 204
        assert response.text == ""
    except EdgeCloudPlatformError as e:
        pytest.fail(f"App undeployment failed: {e}")


# @pytest.mark.parametrize("edgecloud_client", test_cases, ids=id_func, indirect=True)
# def test_timer_wait_5_seconds(edgecloud_client):
#     time.sleep(5)


@pytest.mark.parametrize("edgecloud_client", test_cases, ids=id_func, indirect=True)
def test_delete_onboarded_app(edgecloud_client):
    config = CONFIG[edgecloud_client.client_name]
    try:
        app_id = config["APP_ID"]
        edgecloud_client.delete_onboarded_app(app_id=app_id)
    except EdgeCloudPlatformError as e:
        pytest.fail(f"App onboarding deletion failed: {e}")


@pytest.mark.parametrize("edgecloud_client", test_cases, ids=id_func, indirect=True)
def test_delete_artefact(edgecloud_client):
    config = CONFIG[edgecloud_client.client_name]

    if isinstance(edgecloud_client, I2EdgeClient):
        try:
            edgecloud_client.delete_artefact(artefact_id=config["ARTEFACT_ID"])
        except EdgeCloudPlatformError as e:
            pytest.fail(f"Artefact deletion failed: {e}")
