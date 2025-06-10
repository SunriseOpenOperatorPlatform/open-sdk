# -*- coding: utf-8 -*-
##
# Copyright 2025-present by Software Networks Area, i2CAT.
# All rights reserved.
#
# This file is part of the Open SDK
#
# Contributors:
#   - Adrián Pino Martínez (adrian.pino@i2cat.net)
#   - Sergio Giménez (sergio.gimenez@i2cat.net)
##
"""
EdgeCloud Platform Integration Tests

Validates the complete application lifecycle across multiple clients:
1. Infrastructure (zone discovery)
2. Artefact management (create/delete)
3. Application lifecycle (onboard/deploy/undeploy/delete app onboarded)

Key features:
- Tests all client implementations (parametrized via test_cases)
- Tests configuration available in test_config.py
- Ensures proper resource cleanup
- Uses shared test constants and CAMARA-compliant manifests
- Includes i2edge-specific tests where needed
"""
import time

import pytest

from sunrise6g_opensdk.common.sdk import Sdk as sdkclient
from sunrise6g_opensdk.edgecloud.clients.errors import EdgeCloudPlatformError
from sunrise6g_opensdk.edgecloud.clients.i2edge.client import (
    EdgeApplicationManager as I2EdgeClient,
)
from tests.edgecloud.test_cases import test_cases
from tests.edgecloud.test_config import (
    APP_ID,
    APP_ONBOARD_MANIFEST,
    APP_ZONES,
    ARTEFACT_ID,
    ARTEFACT_NAME,
    REPO_NAME,
    REPO_TYPE,
    REPO_URL,
    ZONE_ID,
)


@pytest.fixture(scope="module", name="edgecloud_client")
def instantiate_edgecloud_client(request):
    """Fixture to create and share an edgecloud client across tests"""
    client_specs = request.param
    clients = sdkclient.create_clients_from(client_specs)
    return clients.get("edgecloud")


def id_func(val):
    return val["edgecloud"]["client_name"]


@pytest.mark.parametrize("edgecloud_client", test_cases, ids=id_func, indirect=True)
def test_get_edge_cloud_zones(edgecloud_client):
    try:
        zones = edgecloud_client.get_edge_cloud_zones()
        assert isinstance(zones, list)
        for zone in zones:
            assert "zoneId" in zone
            assert "geographyDetails" in zone
    except EdgeCloudPlatformError as e:
        pytest.fail(f"Failed to retrieve zones: {e}")


@pytest.mark.parametrize("edgecloud_client", test_cases, ids=id_func, indirect=True)
def test_get_edge_cloud_zones_details(edgecloud_client, zone_id=ZONE_ID):
    """
    Test that get_edge_cloud_zone_details returns valid responses for each client.
    Since each client has different response formats, we only verify basic success criteria.
    """
    try:
        zones = edgecloud_client.get_edge_cloud_zones()
        assert len(zones) > 0, "No zones available for testing"

        zone_details = edgecloud_client.get_edge_cloud_zones_details(zone_id)

        # Basic checks that apply to all clients
        assert zone_details is not None, "Zone details should not be None"
        assert isinstance(zone_details, dict), "Zone details should be a dictionary"
        assert len(zone_details) > 0, "Zone details should not be empty"

    except EdgeCloudPlatformError as e:
        pytest.fail(f"Failed to retrieve zone details: {e}")
    except KeyError as e:
        pytest.fail(f"Missing expected key in response: {e}")


@pytest.mark.parametrize("edgecloud_client", test_cases, ids=id_func, indirect=True)
def test_create_artefact(edgecloud_client):
    if isinstance(edgecloud_client, I2EdgeClient):
        try:
            edgecloud_client._create_artefact(
                artefact_id=ARTEFACT_ID,
                artefact_name=ARTEFACT_NAME,
                repo_name=REPO_NAME,
                repo_type=REPO_TYPE,
                repo_url=REPO_URL,
                password=None,
                token=None,
                user_name=None,
            )
        except EdgeCloudPlatformError as e:
            pytest.fail(f"Artefact creation failed unexpectedly: {e}")


@pytest.mark.parametrize("edgecloud_client", test_cases, ids=id_func, indirect=True)
def test_onboard_app(edgecloud_client):
    try:
        edgecloud_client.onboard_app(APP_ONBOARD_MANIFEST)
    except EdgeCloudPlatformError as e:
        pytest.fail(f"App onboarding failed unexpectedly: {e}")


@pytest.fixture(scope="module")
def app_instance_id(edgecloud_client):
    try:
        output = edgecloud_client.deploy_app(APP_ID, APP_ZONES)
        deployed_app = {"appInstanceId": output["deploy_name"]}
        assert "appInstanceId" in deployed_app
        assert deployed_app["appInstanceId"] is not None
        yield deployed_app["appInstanceId"]
    finally:
        pass


@pytest.mark.parametrize("edgecloud_client", test_cases, ids=id_func, indirect=True)
def test_deploy_app(app_instance_id):
    assert app_instance_id is not None


@pytest.mark.parametrize("edgecloud_client", test_cases, ids=id_func, indirect=True)
def test_timer_wait_30_seconds(edgecloud_client):
    time.sleep(30)


@pytest.mark.parametrize("edgecloud_client", test_cases, ids=id_func, indirect=True)
def test_undeploy_app(edgecloud_client, app_instance_id):
    try:
        edgecloud_client.undeploy_app(app_instance_id)
    except EdgeCloudPlatformError as e:
        pytest.fail(f"App undeployment failed unexpectedly: {e}")


@pytest.mark.parametrize("edgecloud_client", test_cases, ids=id_func, indirect=True)
def test_delete_onboarded_app(edgecloud_client):
    try:
        edgecloud_client.delete_onboarded_app(app_id=APP_ONBOARD_MANIFEST["appId"])
    except EdgeCloudPlatformError as e:
        pytest.fail(f"App onboarding deletion failed unexpectedly: {e}")


@pytest.mark.parametrize("edgecloud_client", test_cases, ids=id_func, indirect=True)
def test_delete_artefact(edgecloud_client):
    if isinstance(edgecloud_client, I2EdgeClient):
        try:
            edgecloud_client._delete_artefact(artefact_id=ARTEFACT_ID)
        except EdgeCloudPlatformError as e:
            pytest.fail(f"Artefact deletion failed unexpectedly: {e}")
