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

from sunrise6g_opensdk.common.sdk import Sdk as sdkclient
from sunrise6g_opensdk.edgecloud.adapters.errors import EdgeCloudPlatformError
from sunrise6g_opensdk.edgecloud.adapters.i2edge.client import (
    EdgeApplicationManager as I2EdgeClient,
)
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
def test_get_edge_cloud_zones(edgecloud_client):
    try:
        zones = edgecloud_client.get_edge_cloud_zones()
        assert isinstance(zones, list)
        # TODO: Harmonise zone schema to match CAMARA schemas across all clients
        if edgecloud_client.client_name == "i2edge":
            for zone in zones:
                assert "zoneId" in zone
                assert "geographyDetails" in zone
        else:
            for zone in zones:
                assert "edgeCloudZoneId" in zone
                assert "edgeCloudZoneName" in zone
                assert "edgeCloudZoneStatus" in zone
                assert "edgeCloudProvider" in zone
                assert "edgeCloudRegion" in zone
    except EdgeCloudPlatformError as e:
        pytest.fail(f"Failed to retrieve zones: {e}")


@pytest.mark.parametrize("edgecloud_client", test_cases, ids=id_func, indirect=True)
def test_get_edge_cloud_zones_details(edgecloud_client):
    config = CONFIG[edgecloud_client.client_name]
    zone_id = config["ZONE_ID"]

    try:
        zones = edgecloud_client.get_edge_cloud_zones()
        assert len(zones) > 0, "No zones available for testing"

        zone_details = edgecloud_client.get_edge_cloud_zones_details(zone_id)

        assert zone_details is not None
        assert isinstance(zone_details, dict)
        assert len(zone_details) > 0

    except (EdgeCloudPlatformError, KeyError) as e:
        pytest.fail(f"Zone detail fetch failed: {e}")


@pytest.mark.parametrize("edgecloud_client", test_cases, ids=id_func, indirect=True)
def test_create_artefact(edgecloud_client):
    config = CONFIG[edgecloud_client.client_name]

    if isinstance(edgecloud_client, I2EdgeClient):
        try:
            edgecloud_client._create_artefact(
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
        edgecloud_client.onboard_app(config["APP_ONBOARD_MANIFEST"])
    except EdgeCloudPlatformError as e:
        pytest.fail(f"App onboarding failed: {e}")


@pytest.fixture(scope="module")
def app_instance_id(edgecloud_client):
    config = CONFIG[edgecloud_client.client_name]
    try:
        output = edgecloud_client.deploy_app(config["APP_ID"], config["APP_ZONES"])

        if edgecloud_client.client_name == "i2edge":
            app_instance_id = output.get("deploy_name")
        else:
            app_instance_id = output.get("appInstanceId")

        assert app_instance_id is not None
        yield app_instance_id
    finally:
        pass


@pytest.mark.parametrize("edgecloud_client", test_cases, ids=id_func, indirect=True)
def test_deploy_app(app_instance_id):
    assert app_instance_id is not None


@pytest.mark.parametrize("edgecloud_client", test_cases, ids=id_func, indirect=True)
def test_timer_wait_60_seconds(edgecloud_client):
    time.sleep(60)


@pytest.mark.parametrize("edgecloud_client", test_cases, ids=id_func, indirect=True)
def test_undeploy_app(edgecloud_client, app_instance_id):
    try:
        edgecloud_client.undeploy_app(app_instance_id)
    except EdgeCloudPlatformError as e:
        pytest.fail(f"App undeployment failed: {e}")


@pytest.mark.parametrize("edgecloud_client", test_cases, ids=id_func, indirect=True)
def test_timer_wait_30_seconds(edgecloud_client):
    time.sleep(30)


@pytest.mark.parametrize("edgecloud_client", test_cases, ids=id_func, indirect=True)
def test_delete_onboarded_app(edgecloud_client):
    config = CONFIG[edgecloud_client.client_name]
    try:
        edgecloud_client.delete_onboarded_app(
            app_id=config["APP_ONBOARD_MANIFEST"]["appId"]
        )
    except EdgeCloudPlatformError as e:
        pytest.fail(f"App onboarding deletion failed: {e}")


@pytest.mark.parametrize("edgecloud_client", test_cases, ids=id_func, indirect=True)
def test_delete_artefact(edgecloud_client):
    config = CONFIG[edgecloud_client.client_name]

    if isinstance(edgecloud_client, I2EdgeClient):
        try:
            edgecloud_client._delete_artefact(artefact_id=config["ARTEFACT_ID"])
        except EdgeCloudPlatformError as e:
            pytest.fail(f"Artefact deletion failed: {e}")
