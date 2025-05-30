# -*- coding: utf-8 -*-
import pytest

from src.network.clients.oai.client import NetworkManager as OaiClient
from src.network.clients.open5gs.client import NetworkManager as Open5GsClient
from src.network.core.network_factory import NetworkClientFactory

test_cases = [
    ("open5gs", "http://192.168.124.233:30769/", "scs"),
    ("oai", "http://127.0.0.1", "scs-oai"),
]


@pytest.mark.parametrize("client_name, base_url, scs_as_id", test_cases)
def test_factory_network(client_name, base_url, scs_as_id):
    """
    Test the factory pattern for the network client.
    """
    client_class_map = {
        "open5gs": Open5GsClient,
        "oai": OaiClient,
    }
    expected_client_class = client_class_map[client_name]
    network_client = NetworkClientFactory.create_network_client(
        client_name, base_url, scs_as_id
    )
    assert isinstance(network_client, expected_client_class)
