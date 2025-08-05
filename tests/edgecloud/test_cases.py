# -*- coding: utf-8 -*-
test_cases = [
    # {
    #     "edgecloud": {
    #         "client_name": "i2edge",
    #         "base_url": "http://X.Y.Z.T:PORT/",
    #         "flavour_id": "<>",
    #     }
    # },
    # {
    #     "edgecloud": {
    #         "client_name": "aeros",
    #         "base_url": "http://X.Y.Z.T:PORT/",
    #         "aerOS_API_URL": "http://A.B.C.D:PORT",
    #         "aerOS_ACCESS_TOKEN": "<>",
    #         "aerOS_HLO_TOKEN": "<>"
    #     }
    # },
    # {
    {
        "edgecloud": {
            "client_name": "kubernetes",
            "base_url": "http://X.Y.Z.T:PORT/",
            # Additional parameters for K8s client:
            "PLATFORM_PROVIDER": "<>",
            "KUBERNETES_MASTER_TOKEN": "<>",
            # "KUBERNETES_MASTER_PORT": "80",
            "KUBERNETES_USERNAME": "<>",
            "EMP_STORAGE_URI": "mongodb://A.B.C.D:PORT",
            "K8S_NAMESPACE": "sunrise6g",
        }
    },
]
