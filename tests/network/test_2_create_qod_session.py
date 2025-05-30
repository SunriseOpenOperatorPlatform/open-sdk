# -*- coding: utf-8 -*-
import pytest

from src.network.core.network_factory import NetworkClientFactory

test_cases = [
    ("open5gs", "http://192.168.124.233:30769/", "scs"),
    ("oai", "http://127.0.0.1:8080/", "scs-oai"),
]


@pytest.mark.parametrize("client_name, base_url, scs_as_id", test_cases)
def test_valid_input(client_name, base_url, scs_as_id):
    network_client = NetworkClientFactory.create_network_client(
        client_name, base_url, scs_as_id
    )

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
    network_client._build_qod_subscription(camara_session)


@pytest.mark.parametrize("client_name, base_url, scs_as_id", test_cases)
def test_create_qod_session(client_name, base_url, scs_as_id):
    network_client = NetworkClientFactory.create_network_client(
        client_name, base_url, scs_as_id
    )

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
