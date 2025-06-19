# -*- coding: utf-8 -*-
import pytest

from sunrise6g_opensdk.common.sdk import Sdk as sdkclient

EDGE_CLOUD_TEST_CASES = [
    {
        "edgecloud": {
            "client_name": "i2edge",
            "base_url": "http://test-nbi-i2edge.sunrise6g",
        }
    },
    {
        "edgecloud": {
            "client_name": "aeros",
            "base_url": "http://test-aeros.url",
            # Additional parameters for aerOS client:
            "aerOS_API_URL": "http://fake.api.url",
            "aerOS_ACCESS_TOKEN": "fake-access",
            "aerOS_HLO_TOKEN": "fake-hlo",
        }
    },
    {
        "edgecloud": {
            "client_name": "piedge",
            "base_url": "",
            # Additional parameters for K8s client:
            "PLATFORM_PROVIDER": "ICOM",
            "KUBERNETES_MASTER_TOKEN": "12345",
            "KUBERNETES_MASTER_PORT": "16443",
            "KUBERNETES_USERNAME": "user",
            # 'EMP_STORAGE_URI': 'http://test.com'
        }
    },
]


def id_func(val):
    return val["edgecloud"]["client_name"]


@pytest.mark.parametrize("client_specs", EDGE_CLOUD_TEST_CASES, ids=id_func)
def test_edgecloud_platform_instantiation(client_specs):
    """Test instantiation of all edgecloud platform clients"""
    clients = sdkclient.create_clients_from(client_specs)

    assert "edgecloud" in clients
    edge_client = clients["edgecloud"]
    assert edge_client is not None
    assert "EdgeApplicationManager" in str(type(edge_client))
