# -*- coding: utf-8 -*-
import pytest

from sunrise6g_opensdk.common.sdk_catalog_client import SdkCatalogClient
from sunrise6g_opensdk.network.clients.open5gs.client import NetworkManager

OPEN5GS_TEST_CASES = [
    {
        "network": {
            "client_name": "open5gs",
            "base_url": "http://192.168.124.233:8082/",
            "scs_as_id": "scs",
        }
    }
]


@pytest.mark.parametrize(
    "client_specs",
    OPEN5GS_TEST_CASES,
    ids=["open5gs"],
)
def test_valid_input_open5gs(client_specs):
    network_client: NetworkManager = SdkCatalogClient.create_clients_from(client_specs)[
        "network"
    ]

    camara_session = {
        "duration": 3600,
        "device": {
            "ipv4Address": {"publicAddress": "10.45.0.3", "privateAddress": "10.45.0.3"}
        },
        "applicationServer": {"ipv4Address": "10.45.0.1"},
        "devicePorts": {"ranges": [{"from": 0, "to": 65535}]},
        "applicationServerPorts": {"ranges": [{"from": 0, "to": 65535}]},
        "qosProfile": "qos-e",
        "sink": "https://endpoint.example.com/sink",
    }
    subscription = network_client._build_qod_subscription(camara_session)
    print(subscription.model_dump_json(exclude_none=True, by_alias=True))


@pytest.mark.parametrize(
    "client_specs",
    OPEN5GS_TEST_CASES,
    ids=["open5gs"],
)
def test_create_qod_session_open5gs(client_specs):
    network_client: NetworkManager = SdkCatalogClient.create_clients_from(client_specs)[
        "network"
    ]

    camara_session = {
        "duration": 3600,
        "device": {
            "ipv4Address": {"publicAddress": "10.45.0.3", "privateAddress": "10.45.0.3"}
        },
        "applicationServer": {"ipv4Address": "10.45.0.1"},
        "devicePorts": {"ranges": [{"from": 0, "to": 65535}]},
        "applicationServerPorts": {"ranges": [{"from": 0, "to": 65535}]},
        "qosProfile": "qos-e",
        "sink": "https://endpoint.example.com/sink",
    }
    network_client.create_qod_session(camara_session)
