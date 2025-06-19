# -*- coding: utf-8 -*-
test_cases = [
    {
        "edgecloud": {
            "client_name": "i2edge",
            "base_url": "http://192.168.123.48:30769/",
        }
    },
    {
        "edgecloud": {
            "client_name": "aeros",
            "base_url": "http://test-aeros.url",
            "aerOS_API_URL": "http://fake.api.url",
            "aerOS_ACCESS_TOKEN": "fake-access",
            "aerOS_HLO_TOKEN": "fake-hlo",
        }
    },
    {
        "edgecloud": {
            "client_name": "piedge",
            "base_url": "http://test-piedge.url",
            "PLATFORM_PROVIDER": "ICOM",
            "KUBERNETES_MASTER_TOKEN": "12345",
            "KUBERNETES_MASTER_PORT": "16443",
            "KUBERNETES_USERNAME": "user",
            "EMP_STORAGE_URI": "http://test.com",
        }
    },
]
