# # -*- coding: utf-8 -*-
import pytest

from sunrise6g_opensdk.network.core.network_factory import NetworkClientFactory

test_cases = [("oai", "http://127.0.0.1/", "scs-oai")]


@pytest.mark.parametrize("client_name, base_url, scs_as_id", test_cases)
def test_valid_input(client_name, base_url, scs_as_id):
    network_client = NetworkClientFactory.create_network_client(
        client_name, base_url, scs_as_id
    )

    ti_session = {
        "device": {
            "ipv4Address": {"publicAddress": "12.1.2.31", "privateAddress": "12.1.2.31"}
        },
        "edgeCloudZoneId": "edge",
        "appId": "testSdk-ffff-aaaa-c0ffe",
        "appInstanceId": "172.21.18.3",
        "notificationUri": "https://endpoint.example.com/sink",
    }
    network_client._build_ti_subscription(ti_session)


@pytest.mark.parametrize("client_name, base_url, scs_as_id", test_cases)
def test_create_traffic_influence(client_name, base_url, scs_as_id):
    network_client = NetworkClientFactory.create_network_client(
        client_name, base_url, scs_as_id
    )

    ti_session = {
        "device": {
            "ipv4Address": {"publicAddress": "12.1.2.31", "privateAddress": "12.1.2.31"}
        },
        "edgeCloudZoneId": "edge",
        "appId": "testSdk-ffff-aaaa-c0ffe",
        "appInstanceId": "172.21.18.3",
        "notificationUri": "https://endpoint.example.com/sink",
    }
    network_client.create_traffic_influence_resource(ti_session)
