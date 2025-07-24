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
            camara_schemas.AppManifest(
                **app_manifest
            )  # Validate against CAMARA AppManifest schema

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
    try:
        response = edgecloud_client.get_edge_cloud_zones()
        assert isinstance(response, Response)
        assert response.status_code == 200
        zones = response.json()
        assert isinstance(zones, list)
        for zone in zones:
            camara_schemas.EdgeCloudZone(**zone)  # Validate against CAMARA model
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
        assert "appId" in payload
        camara_schemas.AppId(root=payload["appId"])

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
        response = edgecloud_client.deploy_app(app_id, app_zones)

        assert isinstance(response, Response)

        # All CAMARA-compliant adapters should return 202 for async deployment
        assert response.status_code == 202

        response_data = response.json()

        # CAMARA spec: response contains appInstances array
        assert "appInstances" in response_data
        assert isinstance(response_data["appInstances"], list)
        assert len(response_data["appInstances"]) > 0

        # Extract appInstanceId from first instance
        app_instance_id = response_data["appInstances"][0].get("appInstanceId")

        assert app_instance_id is not None
        yield app_instance_id
    finally:
        pass


@pytest.mark.parametrize("edgecloud_client", test_cases, ids=id_func, indirect=True)
def test_deploy_app(app_instance_id):
    assert app_instance_id is not None


@pytest.mark.parametrize("edgecloud_client", test_cases, ids=id_func, indirect=True)
def test_timer_wait_10_seconds(edgecloud_client):
    time.sleep(10)


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
