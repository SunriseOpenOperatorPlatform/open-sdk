# -*- coding: utf-8 -*-
test_cases = [
    # {
    #     "edgecloud": {
    #         "client_name": "i2edge",
    #         "base_url": "http://192.168.123.48:30769/",
    #         "flavour_id": "67f3a0b0e3184a85952e174d",
    #     }
    # },
    # {
    #     "edgecloud": {
    #         "client_name": "aeros",
    #         "base_url": "http://test-aeros.url",
    #         "aerOS_API_URL": "http://fake.api.url",
    #         "aerOS_ACCESS_TOKEN": "fake-access",
    #         "aerOS_HLO_TOKEN": "fake-hlo"
    #     }
    # },
    # {
    {
        "edgecloud": {
            "client_name": "kubernetes",
            "base_url": "http://146.124.106.200/k8s",
            # Additional parameters for K8s client:
            "PLATFORM_PROVIDER": "ICOM",
            "KUBERNETES_MASTER_TOKEN": "T3FRNnNVK25FY3I5ZHlNYmxrSEFpd2VPcW5WTlliTnRVNVo3bitNY1B3az0K",
            # "KUBERNETES_MASTER_PORT": "80",
            "KUBERNETES_USERNAME": "user",
            "EMP_STORAGE_URI": "mongodb://146.124.106.200:32411",
        }
    },
]
