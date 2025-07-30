# # -*- coding: utf-8 -*-
import time

import pytest

from sunrise6g_opensdk.common.sdk import Sdk as sdkclient
from sunrise6g_opensdk.network.core.base_network_client import BaseNetworkClient
from sunrise6g_opensdk.network.core.common import CoreHttpError
from tests.network.test_cases import test_cases

ti_session1 = {
    "device": {"ipv4Address": {"publicAddress": "12.1.2.31", "privateAddress": "12.1.2.31"}},
    "edgeCloudZoneId": "edge",
    "appId": "testSdk-ffff-aaaa-c0ffe",
    "appInstanceId": "172.21.18.3",
    "notificationUri": "https://endpoint.example.com/sink",
}

ti_session1_put = {
    "device": {"ipv4Address": {"publicAddress": "12.1.2.31", "privateAddress": "12.1.2.31"}},
    "edgeCloudZoneId": "edge2",
    "appId": "testSdk-ffff-aaaa-c0ffe",
    "appInstanceId": "172.21.18.3",
    "notificationUri": "https://endpoint.example.com/sink",
}

ti_session2 = {
    "device": {"ipv4Address": {"publicAddress": "12.1.2.31", "privateAddress": "12.1.2.31"}},
    "edgeCloudZoneId": "edge",
    "appId": "testSdk-ffff-aaaa-c0ffe",
    "appInstanceId": "172.21.18.65",
    "notificationUri": "https://endpoint.example.com/sink",
}


@pytest.fixture(scope="module", name="network_client")
def instantiate_network_client(request):
    """Fixture to create and share a network client across tests"""
    adapter_specs = request.param
    adapters = sdkclient.create_adapters_from(adapter_specs)
    return adapters.get("network")


def id_func(val):
    return val["network"]["client_name"]


@pytest.mark.parametrize(
    "network_client",
    test_cases,
    ids=id_func,
    indirect=True,
)
def test_valid_input(network_client: BaseNetworkClient):

    network_client._build_ti_subscription(ti_session1)
    network_client._build_ti_subscription(ti_session1_put)

    network_client._build_ti_subscription(ti_session2)


@pytest.fixture(scope="module")
def traffic_influence_id(network_client: BaseNetworkClient):
    try:
        response = network_client.create_traffic_influence_resource(ti_session1)
        assert response is not None, "Response should not be None"
        assert isinstance(response, dict), "Response should be a dictionary"
        assert "trafficInfluenceID" in response, "Response should contain 'trafficInfluenceID'"
        yield str(response["trafficInfluenceID"])
    finally:
        pass


@pytest.fixture(scope="module")
def traffic_influence_id2(network_client: BaseNetworkClient):
    try:
        response = network_client.create_traffic_influence_resource(ti_session2)
        assert response is not None, "Response should not be None"
        assert isinstance(response, dict), "Response should be a dictionary"
        assert "trafficInfluenceID" in response, "Response should contain 'trafficInfluenceID'"
        yield str(response["trafficInfluenceID"])
    finally:
        pass


@pytest.mark.parametrize(
    "network_client",
    test_cases,
    ids=id_func,
    indirect=True,
)
def test_create_traffic_influence_1(traffic_influence_id):
    assert traffic_influence_id is not None


@pytest.mark.parametrize(
    "network_client",
    test_cases,
    ids=id_func,
    indirect=True,
)
def test_create_traffic_influence_2(traffic_influence_id2):
    assert traffic_influence_id2 is not None


@pytest.mark.parametrize("network_client", test_cases, ids=id_func, indirect=True)
def test_timer_wait_5_seconds(network_client):
    time.sleep(5)


@pytest.mark.parametrize("network_client", test_cases, ids=id_func, indirect=True)
def test_get_traffic_influence_session_1(network_client: BaseNetworkClient, traffic_influence_id):
    try:
        response = network_client.get_individual_traffic_influence_resource(traffic_influence_id)
        assert response is not None, "response should not be None"
    except CoreHttpError as e:
        pytest.fail(f"Failed to get traffic influence: {e}")


@pytest.mark.parametrize("network_client", test_cases, ids=id_func, indirect=True)
def test_put_traffic_influence_session_1(network_client: BaseNetworkClient, traffic_influence_id):
    try:
        network_client.put_traffic_influence_resource(traffic_influence_id, ti_session1_put)
    except CoreHttpError as e:
        pytest.fail(f"Failed to update traffic influence session: {e}")


@pytest.mark.parametrize("network_client", test_cases, ids=id_func, indirect=True)
def test_get_traffic_influence_session_after_put_1(
    network_client: BaseNetworkClient, traffic_influence_id
):
    try:
        response = network_client.get_individual_traffic_influence_resource(traffic_influence_id)
        assert response is not None, "response should not be None"
    except CoreHttpError as e:
        pytest.fail(f"Failed to get traffic influence: {e}")


@pytest.mark.parametrize("network_client", test_cases, ids=id_func, indirect=True)
def test_get_all_traffic_influence_sessions(network_client: BaseNetworkClient):
    try:
        response = network_client.get_all_traffic_influence_resource()
        assert response is not None, "response should not be None"
        assert len(response) == 2, "response must containt 2 elements"
    except CoreHttpError as e:
        pytest.fail(f"Failed to get traffic influence: {e}")


@pytest.mark.parametrize("network_client", test_cases, ids=id_func, indirect=True)
def test_delete_traffic_influence_session_1(
    network_client: BaseNetworkClient, traffic_influence_id
):
    try:
        network_client.delete_traffic_influence_resource(traffic_influence_id)
    except CoreHttpError as e:
        pytest.fail(f"Failed to delete traffic influence: {e}")


@pytest.mark.parametrize("network_client", test_cases, ids=id_func, indirect=True)
def test_delete_traffic_influence_session_2(
    network_client: BaseNetworkClient, traffic_influence_id2
):
    try:
        network_client.delete_traffic_influence_resource(traffic_influence_id2)
    except CoreHttpError as e:
        pytest.fail(f"Failed to delete traffic influence: {e}")
