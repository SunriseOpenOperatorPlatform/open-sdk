# -*- coding: utf-8 -*-
import pytest

from sunrise6g_opensdk.common.sdk import Sdk as sdkclient

NETWORK_TEST_CASES = [
    {
        "network": {
            "client_name": "open5gs",
            "base_url": "http://test-open5gs.url",
            "scs_as_id": "scs1",
        }
    },
    {
        "network": {
            "client_name": "oai",
            "base_url": "http://test-oai.url",
            "scs_as_id": "scs2",
        }
    },
    # TODO: Once the functionality from QoD, Location-retrieval and
    # traffic influnce is validated, tests can be carried out for Open5GCore
    # {
    #     "network": {
    #         "client_name": "open5gcore",
    #         "base_url": "http://test-open5gcore.url",
    #         "scs_as_id": "scs3",
    #     }
    # },
]


def id_func(val):
    return val["network"]["client_name"]


@pytest.mark.parametrize("client_specs", NETWORK_TEST_CASES, ids=id_func)
def test_network_platform_instantiation(client_specs):
    """Test instantiation of all network platform clients"""
    clients = sdkclient.create_clients_from(client_specs)

    assert "network" in clients
    network_client = clients["network"]
    assert network_client is not None
    assert "NetworkManager" in str(type(network_client))
