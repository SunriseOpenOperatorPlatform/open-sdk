CONFIG = {
    "i2edge": {
        # Basic identifiers
        "ZONE_ID": "f0662bfe-1d90-5f59-a759-c755b3b69b93",
        "APP_ID": "9c9143f0-f44f-49df-939e-1e8b891ba8f5",
        # Artefact-related fields (non-CAMARA endpoints)
        "ARTEFACT_ID": "9c9143f0-f44f-49df-939e-1e8b891ba8f5",
        "ARTEFACT_NAME": "i2edgechart",
        "REPO_NAME": "github-cesar",
        "REPO_TYPE": "PUBLICREPO",
        "REPO_URL": "https://cesarcajas.github.io/helm-charts-examples/",
        # CAMARA onboard_app payload
        "APP_ONBOARD_MANIFEST": {
            "appId": "9c9143f0-f44f-49df-939e-1e8b891ba8f5",  # Optional to CAMARA
            "name": "i2edge_app_SDK",
            "version": "1.0.0",
            "appProvider": "i2CAT_DEV",
            "packageType": "CONTAINER",
            "appRepo": {
                "type": "PUBLICREPO",
                "imagePath": "https://example.com/my-app-image:1.0.0",
            },
            "requiredResources": {
                "infraKind": "kubernetes",
                "applicationResources": {
                    "cpuPool": {
                        "numCPU": 2,
                        "memory": 2048,
                        "topology": {
                            "minNumberOfNodes": 2,
                            "minNodeCpu": 1,
                            "minNodeMemory": 1024,
                        },
                    }
                },
                "isStandalone": False,
                "version": "1.29",
            },
            "componentSpec": [
                {
                    "componentName": "my-component",
                    "networkInterfaces": [
                        {
                            "interfaceId": "eth0",
                            "protocol": "TCP",
                            "port": 8080,
                            "visibilityType": "VISIBILITY_EXTERNAL",
                        }
                    ],
                }
            ],
        },
        # CAMARA deploy_app payload
        "APP_DEPLOY_PAYLOAD": {
            "appId": "9c9143f0-f44f-49df-939e-1e8b891ba8f5",
            "appZones": [
                {
                    "EdgeCloudZone": {
                        "edgeCloudZoneId": "f0662bfe-1d90-5f59-a759-c755b3b69b93",
                        "edgeCloudZoneName": "i2edge-zone-1",
                        "edgeCloudZoneStatus": "active",
                        "edgeCloudProvider": "i2CAT",
                        "edgeCloudRegion": "Europe-West",
                    }
                }
            ],
        },
    },
    "aeros": {
        # Basic identifiers
        "ZONE_ID": "<UUID>",
        "APP_ID": "<UUID>",
        # CAMARA onboard_app payload
        "APP_ONBOARD_MANIFEST": {
            "appId": "aeros-app-2",
            "name": "aeros-SDK-app",
            "version": "1.0.0",
            "appProvider": "aeros",
            "packageType": "CONTAINER",
            "appRepo": {
                "type": "PUBLICREPO",
                "imagePath": "docker.io/library/nginx:stable",
            },
            "requiredResources": {
                "infraKind": "kubernetes",
                "applicationResources": {
                    "cpuPool": {
                        "numCPU": 1,
                        "memory": 1024,
                        "topology": {
                            "minNumberOfNodes": 1,
                            "minNodeCpu": 1,
                            "minNodeMemory": 512,
                        },
                    }
                },
                "isStandalone": True,
                "version": "1.28",
            },
            "componentSpec": [
                {
                    "componentName": "aeros-component",
                    "networkInterfaces": [
                        {
                            "interfaceId": "eth0",
                            "protocol": "TCP",
                            "port": 9090,
                            "visibilityType": "VISIBILITY_INTERNAL",
                        }
                    ],
                }
            ],
        },
        # CAMARA deploy_app payload
        "APP_DEPLOY_PAYLOAD": {
            "appId": "aeros-app-2",
            "appZones": [
                {
                    "EdgeCloudZone": {
                        "edgeCloudZoneId": "urn:ngsi-ld:Domain:NCSRD",
                        "edgeCloudZoneName": "aeros-zone-1",
                        "edgeCloudZoneStatus": "active",
                        "edgeCloudProvider": "NCSRD",
                        "edgeCloudRegion": "Europe-South",
                    }
                }
            ],
        },
    },
    "kubernetes": {
        # Basic identifiers
        "ZONE_ID": "999b7746-d2e2-4bb4-96e6-f1e895adef0c",
        "APP_ID": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "ZONE_ID": "999b7746-d2e2-4bb4-96e6-f1e895adef0c",
        "APP_DEPLOY_PAYLOAD": {
            "appId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "appZones": [
                {
                    "EdgeCloudZone": {
                        "edgeCloudZoneId": "999b7746-d2e2-4bb4-96e6-f1e895adef0c",
                        "edgeCloudZoneName": "zorro-solutions",
                        "edgeCloudZoneStatus": "active",
                        "edgeCloudProvider": "ICOM",
                        "edgeCloudRegion": "Europe-Southeast",
                    }
                }
            ],
        },
        # CAMARA deploy_app payload
        # "APP_DEPLOY_PAYLOAD": {
        #     "appId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        #     "name": "nginx-test",
        #     "edgeCloudZoneId": "zorro-solutions",
        #     "kubernetesClusterRef": "",
        # },
        # Legacy K8S_DEPLOY_PAYLOAD for backward compatibility (if needed)
        "K8S_DEPLOY_PAYLOAD": {
            "appId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "name": "nginx-test",
            "edgeCloudZoneId": "zorro-solutions",
            "kubernetesClusterRef": "",
        },
        "APP_ONBOARD_MANIFEST": {
            "appId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "name": "nginx_test",
            "version": "1",
            "packageType": "QCOW2",
            "appProvider": "jJsxUU403g5PUhoRtYfOBaaIRZGVzXDZgMBqzMYq5xLcdZoWGYIYqmVy0",
            "appRepo": {"imagePath": "nginx", "type": "PRIVATEREPO"},
            "requiredResources": {
                "infraKind": "kubernetes",
                "applicationResources": {
                    "cpuPool": {
                        "numCPU": 2,
                        "memory": 2048,
                        "topology": {
                            "minNumberOfNodes": 2,
                            "minNodeCpu": 1,
                            "minNodeMemory": 1024,
                        },
                    }
                },
                "isStandalone": False,
                "version": "1.29",
            },
            "componentSpec": [
                {
                    "componentName": "nginx",
                    "networkInterfaces": [
                        {
                            "protocol": "TCP",
                            "port": 80,
                            "interfaceId": "Uj6qThvzkegxa3L4b88",
                            "visibilityType": "VISIBILITY_EXTERNAL",
                        },
                        {
                            "protocol": "TCP",
                            "port": 443,
                            "interfaceId": "Uj6qThvzkegxa3L4b88",
                            "visibilityType": "VISIBILITY_EXTERNAL",
                        },
                    ],
                }
            ],
        },
        # CAMARA deploy_app payload
    },
}
