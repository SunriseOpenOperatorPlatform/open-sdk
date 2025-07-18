# from sunrise6g_opensdk import Sdk as sdkclient # For PyPI users
import time

from sunrise6g_opensdk.common.sdk import Sdk as sdkclient  # For developers


def main():
    # The module that imports the SDK package, must specify which adapters will be used:
    adapter_specs = {
        "edgecloud": {
            "client_name": "i2edge",
            "base_url": "http://192.168.123.48:30769",
            "flavour_id": "67f3a0b0e3184a85952e174d",
        },
        "network": {
            "client_name": "open5gs",
            "base_url": "http://IP:PORT",
            "scs_as_id": "id_example",
        },
    }

    adapters = sdkclient.create_adapters_from(adapter_specs)
    edgecloud_client = adapters.get("edgecloud")
    network_client = adapters.get("network")

    print("EdgeCloud client ready to be used:", edgecloud_client.__dict__)
    print("Network client ready to be used:", network_client)

    # Examples:
    # EdgeCloud

    # FederationManagement

    zones_list = edgecloud_client.get_edge_cloud_zones_list_gsma()
    print(zones_list)
    print(zones_list.status_code)
    print(zones_list.json())

    zones = edgecloud_client.get_edge_cloud_zones_gsma("federation_context_id")
    print(zones)
    print(zones.status_code)
    print(zones.json())

    # AvailabilityZoneInfoSynchronization

    zones_info = edgecloud_client.availability_zone_info_gsma(
        "federation_context_id", {"request_body": "value"}
    )
    print(zones_info)
    print(zones_info.status_code)
    print(zones_info.json())

    zone_id = "Omega"
    zones = edgecloud_client.get_edge_cloud_zone_details_gsma(
        "federation_context_id", zone_id
    )
    print(zones)
    print(zones.status_code)
    print(zones.json())

    # ArtefactManager

    request_body = {
        "artefactId": "i2edgechart",
        "appProviderId": "string",
        "artefactName": "i2edgechart",
        "artefactVersionInfo": "string",
        "artefactDescription": "string",
        "artefactVirtType": "VM_TYPE",
        "artefactFileName": "string",
        "artefactFileFormat": "WINZIP",
        "artefactDescriptorType": "HELM",
        "repoType": "PUBLICREPO",
        "artefactRepoLocation": {
            "repoURL": "https://cesarcajas.github.io/helm-charts-examples/",
            "userName": "string",
            "password": "string",
            "token": "string",
        },
        "artefactFile": "string",
        "componentSpec": [
            {
                "componentName": "string",
                "images": ["3fa85f64-5717-4562-b3fc-2c963f66afa6"],
                "numOfInstances": 0,
                "restartPolicy": "RESTART_POLICY_ALWAYS",
                "commandLineParams": {"command": ["string"], "commandArgs": ["string"]},
                "exposedInterfaces": [
                    {
                        "interfaceId": "string",
                        "commProtocol": "TCP",
                        "commPort": 0,
                        "visibilityType": "VISIBILITY_EXTERNAL",
                        "network": "string",
                        "InterfaceName": "string",
                    }
                ],
                "computeResourceProfile": {
                    "cpuArchType": "ISA_X86_64",
                    "numCPU": {
                        "whole": {"value": 2},
                        "decimal": {"value": 0.5},
                        "millivcpu": {"value": "500m"},
                    },
                    "memory": 0,
                    "diskStorage": 0,
                    "gpu": [
                        {
                            "gpuVendorType": "GPU_PROVIDER_NVIDIA",
                            "gpuModeName": "string",
                            "gpuMemory": 0,
                            "numGPU": 0,
                        }
                    ],
                    "vpu": 0,
                    "fpga": 0,
                    "hugepages": [{"pageSize": "2MB", "number": 0}],
                    "cpuExclusivity": True,
                },
                "compEnvParams": [
                    {
                        "envVarName": "string",
                        "envValueType": "USER_DEFINED",
                        "envVarValue": "string",
                        "envVarSrc": "string",
                    }
                ],
                "deploymentConfig": {
                    "configType": "DOCKER_COMPOSE",
                    "contents": "string",
                },
                "persistentVolumes": [
                    {
                        "volumeSize": "10Gi",
                        "volumeMountPath": "string",
                        "volumeName": "string",
                        "ephemeralType": False,
                        "accessMode": "RW",
                        "sharingPolicy": "EXCLUSIVE",
                    }
                ],
            }
        ],
    }
    artefact = edgecloud_client.create_artefact_gsma(
        "federation_context_id", request_body
    )
    print(artefact)
    print(artefact.status_code)
    print(artefact.json())

    artefact_id = "i2edgechart"
    get_artefact = edgecloud_client.get_artefact_gsma(
        "federation_context_id", artefact_id
    )
    print(get_artefact)
    print(get_artefact.status_code)
    print(get_artefact.json())

    # ApplicationOnboardingManager

    request_body = {
        "appId": "demo-app-id",
        "appProviderId": "Y89TSlxMPDKlXZz7rN6vU2y",
        "appDeploymentZones": [
            "Dmgoc-y2zv97lar0UKqQd53aS6MCTTdoGMY193yvRBYgI07zOAIktN2b9QB2THbl5Gqvbj5Zp92vmNeg7v4M"
        ],
        "appMetaData": {
            "appName": "pj1iEkprop",
            "version": "string",
            "appDescription": "stringstringstri",
            "mobilitySupport": False,
            "accessToken": "MfxADOjxDgBhMrqmBeG8XdQFLp2XviG3cZ_LM7uQKc9b",
            "category": "IOT",
        },
        "appQoSProfile": {
            "latencyConstraints": "NONE",
            "bandwidthRequired": 1,
            "multiUserClients": "APP_TYPE_SINGLE_USER",
            "noOfUsersPerAppInst": 1,
            "appProvisioning": True,
        },
        "appComponentSpecs": [
            {
                "serviceNameNB": "k8yyElSyJN4ctbNVqwodEQNUoGb2EzOEt4vQBjGnPii_5",
                "serviceNameEW": "iDm08OZN",
                "componentName": "HIEWqstajCmZJQmSFUj0kNHZ0xYvKWq720BKt8wjA41p",
                "artefactId": "i2edgechart",
            }
        ],
        "appStatusCallbackLink": "string",
        "edgeAppFQDN": "string",
    }
    onboard_app = edgecloud_client.onboard_app_gsma(
        "federation_context_id", request_body
    )
    print(onboard_app)
    print(onboard_app.status_code)
    print(onboard_app.json())

    app_id = "demo-app-id"
    get_onboarded_app = edgecloud_client.get_onboarded_app_gsma(
        "federation_context_id", app_id
    )
    print(get_onboarded_app)
    print(get_onboarded_app.status_code)
    print(get_onboarded_app.json())

    idempotency_key = "idempotency-key"
    request_body = {
        "appId": "demo-app-id",
        "appVersion": "string",
        "appProviderId": "Y89TSlxMPDKlXZz7rN6vU2y",
        "zoneInfo": {
            "zoneId": "Omega",
            "flavourId": "67f3a0b0e3184a85952e174d",
            "resourceConsumption": "RESERVED_RES_AVOID",
            "resPool": "ySIT0LuZ6ApHs0wlyGZve",
        },
        "appInstCallbackLink": "string",
    }
    deploy_app = edgecloud_client.deploy_app_gsma(
        "federation_context_id", idempotency_key, request_body
    )
    app_instance_id = deploy_app.json().get("appInstIdentifier")
    print(deploy_app)
    print(deploy_app.status_code)
    print(deploy_app.json())

    time.sleep(10)

    app_id = "demo-app-id"
    zone_id = "Omega"
    get_deploy_app = edgecloud_client.get_deployed_app_gsma(
        "federation_context_id", app_id, app_instance_id, zone_id
    )
    print(get_deploy_app)
    print(get_deploy_app.status_code)
    print(get_deploy_app.json())

    get_deployed_apps = edgecloud_client.get_all_deployed_apps_gsma(
        "federation_context_id", app_id, "app_provider"
    )
    print(get_deployed_apps)
    print(get_deployed_apps.status_code)
    print(get_deployed_apps.json())

    app_id = "demo-app-id"
    zone_id = "Omega"
    delete_deploy_app = edgecloud_client.undeploy_app_gsma(
        "federation_context_id", app_id, app_instance_id, zone_id
    )
    print(delete_deploy_app)
    print(delete_deploy_app.status_code)
    print(delete_deploy_app.json())

    app_id = "demo-app-id"
    delete_onboarded_app = edgecloud_client.delete_onboarded_app_gsma(
        "federation_context_id", app_id
    )
    print(delete_onboarded_app)
    print(delete_onboarded_app.status_code)
    print(delete_onboarded_app.json())

    artefact_id = "i2edgechart"
    delete_artefact = edgecloud_client.delete_artefact_gsma(
        "federation_context_id", artefact_id
    )
    print(delete_artefact)
    print(delete_artefact.status_code)
    print(delete_artefact.json())

    # Network
    print("Testing network client function: 'get_qod_session'")
    network_client.get_qod_session(session_id="example_session_id")


if __name__ == "__main__":
    main()
