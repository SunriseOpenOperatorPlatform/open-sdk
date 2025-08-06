##
# This file is part of the Open SDK
#
# Contributors:
#   - Vasilis Pitsilis (vpitsilis@dat.demokritos.gr, vpitsilis@iit.demokritos.gr)
#   - Andreas Sakellaropoulos (asakellaropoulos@iit.demokritos.gr)
##
import uuid
from typing import Any, Dict, List, Optional

import yaml
from requests import Response

from sunrise6g_opensdk.edgecloud.adapters.aeros import config
from sunrise6g_opensdk.edgecloud.adapters.aeros.continuum_client import ContinuumClient
from sunrise6g_opensdk.edgecloud.adapters.errors import EdgeCloudPlatformError
from sunrise6g_opensdk.edgecloud.core.edgecloud_interface import (
    EdgeCloudManagementInterface,
)
from sunrise6g_opensdk.logger import setup_logger


class EdgeApplicationManager(EdgeCloudManagementInterface):
    """
    aerOS Continuum Client
    FIXME: Handle None responses from continuum client
    """

    def __init__(self, base_url: str, **kwargs):
        self.base_url = base_url
        self.logger = setup_logger(__name__, is_debug=True, file_name=config.LOG_FILE)
        self._app_store: Dict[str, Dict] = {}
        self._deployed_services: Dict[str, List[str]] = {}
        self._stopped_services: Dict[str, List[str]] = {}

        # Overwrite config values if provided via kwargs
        if "aerOS_API_URL" in kwargs:
            config.aerOS_API_URL = kwargs["aerOS_API_URL"]
        if "aerOS_ACCESS_TOKEN" in kwargs:
            config.aerOS_ACCESS_TOKEN = kwargs["aerOS_ACCESS_TOKEN"]
        if "aerOS_HLO_TOKEN" in kwargs:
            config.aerOS_HLO_TOKEN = kwargs["aerOS_HLO_TOKEN"]

        if not config.aerOS_API_URL:
            raise ValueError("Missing 'aerOS_API_URL'")
        if not config.aerOS_ACCESS_TOKEN:
            raise ValueError("Missing 'aerOS_ACCESS_TOKEN'")
        if not config.aerOS_HLO_TOKEN:
            raise ValueError("Missing 'aerOS_HLO_TOKEN'")

    def onboard_app(self, app_manifest: Dict) -> Dict:
        app_id = app_manifest.get("appId")
        if not app_id:
            raise EdgeCloudPlatformError("Missing 'appId' in app manifest")

        if app_id in self._app_store:
            raise EdgeCloudPlatformError(f"Application with id '{app_id}' already exists")

        self._app_store[app_id] = app_manifest
        self.logger.debug("Onboarded application with id: %s", app_id)
        return {"appId": app_id}

    def get_all_onboarded_apps(self) -> List[Dict]:
        self.logger.debug("Onboarded applications: %s", list(self._app_store.keys()))
        return list(self._app_store.values())

    def get_onboarded_app(self, app_id: str) -> Dict:
        if app_id not in self._app_store:
            raise EdgeCloudPlatformError(f"Application with id '{app_id}' does not exist")
        self.logger.debug("Retrieved application with id: %s", app_id)
        return self._app_store[app_id]

    def delete_onboarded_app(self, app_id: str) -> None:
        if app_id not in self._app_store:
            raise EdgeCloudPlatformError(f"Application with id '{app_id}' does not exist")
        service_instances = self._stopped_services.get(app_id, [])
        self.logger.debug(
            "Deleting application with id: %s and instances: %s",
            app_id,
            service_instances,
        )
        for service_instance in service_instances:
            self._purge_deployed_app_from_continuum(service_instance)
            self.logger.debug("successfully purged service instance: %s", service_instance)
        del self._stopped_services[app_id]  # Clean up stopped services
        del self._app_store[app_id]  # Remove from onboarded apps

    def _generate_service_id(self, app_id: str) -> str:
        return f"urn:ngsi-ld:Service:{app_id}-{uuid.uuid4().hex[:4]}"

    def _generate_tosca_yaml_dict(self, app_manifest: Dict, app_zones: List[Dict]) -> Dict:
        component = app_manifest.get("componentSpec", [{}])[0]
        component_name = component.get("componentName", "application")

        image_path = app_manifest.get("appRepo", {}).get("imagePath", "")
        image_file = image_path.split("/")[-1]
        repository_url = "/".join(image_path.split("/")[:-1]) if "/" in image_path else "docker_hub"
        zone_id = app_zones[0].get("EdgeCloudZone", {}).get("edgeCloudZoneId", "default-zone")

        # Extract minNodeMemory
        min_node_memory = (
            app_manifest.get("requiredResources", {})
            .get("applicationResources", {})
            .get("cpuPool", {})
            .get("topology", {})
            .get("minNodeMemory", 1024)
        )

        ports = {}
        for iface in component.get("networkInterfaces", []):
            interface_id = iface.get("interfaceId", "default")
            protocol = iface.get("protocol", "TCP").lower()
            port = iface.get("port", 8080)
            ports[interface_id] = {"properties": {"protocol": [protocol], "source": port}}

        expose_ports = any(
            iface.get("visibilityType") == "VISIBILITY_EXTERNAL"
            for iface in component.get("networkInterfaces", [])
        )

        yaml_dict = {
            "tosca_definitions_version": "tosca_simple_yaml_1_3",
            "description": f"TOSCA for {app_manifest.get('name', 'application')}",
            "serviceOverlay": False,
            "node_templates": {
                component_name: {
                    "type": "tosca.nodes.Container.Application",
                    "isJob": False,
                    "requirements": [
                        {
                            "network": {
                                "properties": {
                                    "ports": ports,
                                    "exposePorts": expose_ports,
                                }
                            }
                        },
                        {
                            "host": {
                                "node_filter": {
                                    "capabilities": [
                                        {
                                            "host": {
                                                "properties": {
                                                    "cpu_arch": {"equal": "x64"},
                                                    "realtime": {"equal": False},
                                                    "cpu_usage": {"less_or_equal": "0.1"},
                                                    "mem_size": {
                                                        "greater_or_equal": str(min_node_memory)
                                                    },
                                                    "domain_id": {"equal": zone_id},
                                                }
                                            }
                                        }
                                    ],
                                    "properties": None,
                                }
                            }
                        },
                    ],
                    "artifacts": {
                        "application_image": {
                            "file": image_file,
                            "type": "tosca.artifacts.Deployment.Image.Container.Docker",
                            "is_private": False,
                            "repository": repository_url,
                        }
                    },
                    "interfaces": {
                        "Standard": {
                            "create": {
                                "implementation": "application_image",
                                "inputs": {"cliArgs": [], "envVars": []},
                            }
                        }
                    },
                }
            },
        }

        return yaml_dict

    def deploy_app(self, app_id: str, app_zones: List[Dict]) -> Dict:
        # 1. Get app CAMARA manifest
        app_manifest = self._app_store.get(app_id)
        if not app_manifest:
            raise EdgeCloudPlatformError(f"Application with id '{app_id}' does not exist")

        # 2. Generate unique service ID
        service_id = self._generate_service_id(app_id)

        # 3. Convert dict to YAML string
        yaml_dict = self._generate_tosca_yaml_dict(app_manifest, app_zones)
        tosca_yaml = yaml.dump(yaml_dict, sort_keys=False)
        self.logger.info("Generated TOSCA YAML:")
        self.logger.info(tosca_yaml)

        # 4. Instantiate client and call continuum to deploy service
        aeros_client = ContinuumClient(self.base_url)
        response = aeros_client.onboard_and_deploy_service(service_id, tosca_yaml)

        if "serviceId" not in response:
            raise EdgeCloudPlatformError(
                "Invalid response from onboard_service: missing 'serviceId'"
            )

        # 5. Track deployment
        if app_id not in self._deployed_services:
            self._deployed_services[app_id] = []
        self._deployed_services[app_id].append(service_id)

        # 6. Return expected format
        return {"appInstanceId": response["serviceId"]}

    def get_all_deployed_apps(
        self,
        app_id: Optional[str] = None,
        app_instance_id: Optional[str] = None,
        region: Optional[str] = None,
    ) -> List[Dict]:
        deployed = []
        for stored_app_id, instance_ids in self._deployed_services.items():
            for instance_id in instance_ids:
                deployed.append({"appId": stored_app_id, "appInstanceId": instance_id})
        return deployed

    def get_deployed_app(
        self, app_instance_id: str, app_id: Optional[str] = None, region: Optional[str] = None
    ) -> Response:
        """
        Placeholder implementation for CAMARA compliance.
        Retrieves information of a specific application instance.

        :param app_instance_id: Unique identifier of the application instance
        :param app_id: Optional filter by application ID
        :param region: Optional filter by Edge Cloud region
        :return: Response with application instance details
        """
        # TODO: Implement actual aeros-specific logic for retrieving a specific deployed app
        raise NotImplementedError("get_deployed_app is not yet implemented for aeros adapter")

    def _purge_deployed_app_from_continuum(self, app_id: str) -> None:
        aeros_client = ContinuumClient(self.base_url)
        response = aeros_client.purge_service(app_id)
        if response:
            self.logger.debug("Purged deployed application with id: %s", app_id)
        else:
            raise EdgeCloudPlatformError(
                f"Failed to purg service with id from the continuum '{app_id}'"
            )

    def undeploy_app(self, app_instance_id: str) -> None:
        # 1. Locate app_id corresponding to this instance
        found_app_id = None
        for app_id, instances in self._deployed_services.items():
            if app_instance_id in instances:
                found_app_id = app_id
                break

        if not found_app_id:
            raise EdgeCloudPlatformError(
                f"No deployed app instance with ID '{app_instance_id}' found"
            )

        # 2. Call the external undeploy_service
        aeros_client = ContinuumClient(self.base_url)
        try:
            aeros_client.undeploy_service(app_instance_id)
        except Exception as e:
            raise EdgeCloudPlatformError(
                f"Failed to undeploy app instance '{app_instance_id}': {str(e)}"
            ) from e

        # We could do it here with a little wait but better all instances in the same app are purged at once
        # 3. Purge the deployed app from continuum
        # self._purge_deployed_app_from_continuum(app_instance_id)

        # 4. Clean up internal tracking
        self._deployed_services[found_app_id].remove(app_instance_id)
        # Add instance to _stopped_services to purge it later
        if found_app_id not in self._stopped_services:
            self._stopped_services[found_app_id] = []
        self._stopped_services[found_app_id].append(app_instance_id)
        # If app has no instances left, remove it from deployed services
        if not self._deployed_services[found_app_id]:
            del self._deployed_services[found_app_id]

    def get_edge_cloud_zones(
        self, region: Optional[str] = None, status: Optional[str] = None
    ) -> List[Dict]:
        aeros_client = ContinuumClient(self.base_url)
        ngsild_params = "type=Domain&format=simplified"
        aeros_domains = aeros_client.query_entities(ngsild_params)
        return [
            {
                "zoneId": domain["id"],
                "status": domain["domainStatus"].split(":")[-1].lower(),
                "geographyDetails": "NOT_USED",
            }
            for domain in aeros_domains
        ]

    def get_edge_cloud_zones_details(self, zone_id: str, flavour_id: Optional[str] = None) -> Dict:
        """
        Get details of a specific edge cloud zone.
        :param zone_id: The ID of the edge cloud zone
        :param flavour_id: Optional flavour ID to filter the results
        :return: Details of the edge cloud zone
        """
        # Minimal mocked response based on required fields of 'ZoneRegisteredData' in GSMA OPG E/WBI API
        # return {
        #     "zoneId":
        #     zone_id,
        #     "reservedComputeResources": [{
        #         "cpuArchType": "ISA_X86_64",
        #         "numCPU": "4",
        #         "memory": 8192,
        #     }],
        #     "computeResourceQuotaLimits": [{
        #         "cpuArchType": "ISA_X86_64",
        #         "numCPU": "8",
        #         "memory": 16384,
        #     }],
        #     "flavoursSupported": [{
        #         "flavourId":
        #         "medium-x86",
        #         "cpuArchType":
        #         "ISA_X86_64",
        #         "supportedOSTypes": [{
        #             "architecture": "x86_64",
        #             "distribution": "UBUNTU",
        #             "version": "OS_VERSION_UBUNTU_2204_LTS",
        #             "license": "OS_LICENSE_TYPE_FREE",
        #         }],
        #         "numCPU":
        #         4,
        #         "memorySize":
        #         8192,
        #         "storageSize":
        #         100,
        #     }],
        #     #
        # }
        aeros_client = ContinuumClient(self.base_url)
        ngsild_params = f'format=simplified&type=InfrastructureElement&q=domain=="{zone_id}"'
        self.logger.debug(
            "Querying infrastructure elements for zone %s with params: %s",
            zone_id,
            ngsild_params,
        )
        # Query the infrastructure elements for the specified zonese
        aeros_domain_ies = aeros_client.query_entities(ngsild_params)
        # Transform the infrastructure elements into the required format
        # and return the details of the edge cloud zone
        response = self.transform_infrastructure_elements(
            domain_ies=aeros_domain_ies, domain=zone_id
        )
        self.logger.debug("Transformed response: %s", response)
        # Return the transformed response
        return response

    def transform_infrastructure_elements(
        self, domain_ies: List[Dict[str, Any]], domain: str
    ) -> Dict[str, Any]:
        """
        Transform the infrastructure elements into a format suitable for the
        edge cloud zone details.
        :param domain_ies: List of infrastructure elements
        :param domain: The ID of the edge cloud zone
        :return: Transformed details of the edge cloud zone
        """
        total_cpu = 0
        total_ram = 0
        total_disk = 0
        total_available_ram = 0
        total_available_disk = 0

        flavours_supported = []

        for element in domain_ies:
            total_cpu += element.get("cpuCores", 0)
            total_ram += element.get("ramCapacity", 0)
            total_available_ram += element.get("availableRam", 0)
            total_disk += element.get("diskCapacity", 0)
            total_available_disk += element.get("availableDisk", 0)

            # Create a flavour per machine
            flavour = {
                "flavourId": f"{element.get('hostname')}-{element.get('containerTechnology')}",
                "cpuArchType": f"{element.get('cpuArchitecture')}",
                "supportedOSTypes": [
                    {
                        "architecture": f"{element.get('cpuArchitecture')}",
                        "distribution": f"{element.get('operatingSystem')}",  # assume
                        "version": "OS_VERSION_UBUNTU_2204_LTS",
                        "license": "OS_LICENSE_TYPE_FREE",
                    }
                ],
                "numCPU": element.get("cpuCores", 0),
                "memorySize": element.get("ramCapacity", 0),
                "storageSize": element.get("diskCapacity", 0),
            }
            flavours_supported.append(flavour)

        result = {
            "zoneId": domain,
            "reservedComputeResources": [
                {
                    "cpuArchType": "ISA_X86_64",
                    "numCPU": str(total_cpu),
                    "memory": total_ram,
                }
            ],
            "computeResourceQuotaLimits": [
                {
                    "cpuArchType": "ISA_X86_64",
                    "numCPU": str(total_cpu * 2),  # Assume quota is 2x total?
                    "memory": total_ram * 2,
                }
            ],
            "flavoursSupported": flavours_supported,
        }
        return result

    # --- GSMA-specific methods ---

    # FederationManagement

    def get_edge_cloud_zones_list_gsma(self) -> List:
        """
        Retrieves list of all Zones

        :return: List.
        """
        pass

    # AvailabilityZoneInfoSynchronization

    def get_edge_cloud_zones_gsma(self) -> List:
        """
        Retrieves details of all Zones

        :return: List.
        """
        pass

    def get_edge_cloud_zone_details_gsma(self, zone_id: str) -> Dict:
        """
        Retrieves details of a specific Edge Cloud Zone reserved
        for the specified zone by the partner OP.

        :param zone_id: Unique identifier of the Edge Cloud Zone.
        :return: Dictionary with Edge Cloud Zone details.
        """
        pass

    # ArtefactManagement

    def create_artefact_gsma(self, request_body: dict):
        """
        Uploads application artefact on partner OP. Artefact is a zip file
        containing scripts and/or packaging files like Terraform or Helm
        which are required to create an instance of an application

        :param request_body: Payload with artefact information.
        :return:
        """
        pass

    def get_artefact_gsma(self, artefact_id: str) -> Dict:
        """
        Retrieves details about an artefact

        :param artefact_id: Unique identifier of the artefact.
        :return: Dictionary with artefact details.
        """
        pass

    def delete_artefact_gsma(self, artefact_id: str):
        """
        Removes an artefact from partners OP.

        :param artefact_id: Unique identifier of the artefact.
        :return:
        """
        pass

    # ApplicationOnboardingManagement

    def onboard_app_gsma(self, request_body: dict):
        """
        Submits an application details to a partner OP.
        Based on the details provided, partner OP shall do bookkeeping,
        resource validation and other pre-deployment operations.

        :param request_body: Payload with onboarding info.
        :return:
        """
        pass

    def get_onboarded_app_gsma(self, app_id: str) -> Dict:
        """
        Retrieves application details from partner OP

        :param app_id: Identifier of the application onboarded.
        :return: Dictionary with application details.
        """
        pass

    def patch_onboarded_app_gsma(self, app_id: str, request_body: dict):
        """
        Updates partner OP about changes in application compute resource requirements,
        QOS Profile, associated descriptor or change in associated components

        :param app_id: Identifier of the application onboarded.
        :param request_body: Payload with updated onboarding info.
        :return:
        """
        pass

    def delete_onboarded_app_gsma(self, app_id: str):
        """
        Deboards an application from specific partner OP zones

        :param app_id: Identifier of the application onboarded.
        :return:
        """
        pass

    # ApplicationDeploymentManagement

    def deploy_app_gsma(self, request_body: dict) -> Dict:
        """
        Instantiates an application on a partner OP zone.

        :param request_body: Payload with deployment info.
        :return: Dictionary with deployment details.
        """
        pass

    def get_deployed_app_gsma(self, app_id: str, app_instance_id: str, zone_id: str) -> Dict:
        """
        Retrieves an application instance details from partner OP.

        :param app_id: Identifier of the app.
        :param app_instance_id: Identifier of the deployed instance.
        :param zone_id: Identifier of the zone
        :return: Dictionary with application instance details
        """
        pass

    def get_all_deployed_apps_gsma(self) -> Response:
        """
        Retrieves all instances for a given application of partner OP

        :param app_id: Identifier of the app.
        :param app_provider: App provider
        :return: List with application instances details
        """
        pass

    def undeploy_app_gsma(self, app_id: str, app_instance_id: str, zone_id: str):
        """
        Terminate an application instance on a partner OP zone.

        :param app_id: Identifier of the app.
        :param app_instance_id: Identifier of the deployed app.
        :param zone_id: Identifier of the zone
        :return:
        """
        pass
