##
# This file is part of the Open SDK
#
# Contributors:
#   - Vasilis Pitsilis (vpitsilis@dat.demokritos.gr, vpitsilis@iit.demokritos.gr)
#   - Andreas Sakellaropoulos (asakellaropoulos@iit.demokritos.gr)
##
from typing import Any, Dict, List, Optional

from sunrise6g_opensdk.edgecloud.clients.aeros import config
from sunrise6g_opensdk.edgecloud.clients.aeros.continuum_client import ContinuumClient
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
        # HLO-FE POST with TOSCA and app_id (service_id)
        service_id = app_manifest.get("serviceId")
        tosca_str = app_manifest.get("tosca")
        aeros_client = ContinuumClient(self.base_url)
        onboard_response = aeros_client.onboard_service(
            service_id=service_id, tosca_str=tosca_str
        )
        return {"appId": onboard_response["serviceId"]}

    def get_all_onboarded_apps(self) -> List[Dict]:
        aeros_client = ContinuumClient(self.base_url)
        ngsild_params = "type=Service&format=simplified"
        aeros_apps = aeros_client.query_entities(ngsild_params)
        return [
            {"appId": service["id"], "name": service["name"]} for service in aeros_apps
        ]
        # return [{"appId": "1234-5678", "name": "TestApp"}]

    def get_onboarded_app(self, app_id: str) -> Dict:
        aeros_client = ContinuumClient(self.base_url)
        ngsild_params = "format=simplified"
        aeros_app = aeros_client.query_entity(app_id, ngsild_params)
        return {"appId": aeros_app["id"], "name": aeros_app["name"]}

    def delete_onboarded_app(self, app_id: str) -> None:
        print(f"Deleting application: {app_id}")
        # TBD: Purge from continuum (make all ngsil-ld calls for servieId connected entities)
        # Should check if undeployed first

    def deploy_app(self, app_id: str, app_zones: List[Dict]) -> Dict:
        # HLO-FE PUT with app_id (service_id)
        aeros_client = ContinuumClient(self.base_url)
        deploy_response = aeros_client.deploy_service(app_id)
        return {"appInstanceId": deploy_response["serviceId"]}

    def get_all_deployed_apps(
        self,
        app_id: Optional[str] = None,
        app_instance_id: Optional[str] = None,
        region: Optional[str] = None,
    ) -> List[Dict]:
        # FIXME: Get services in deployed state
        aeros_client = ContinuumClient(self.base_url)
        ngsild_params = 'type=Service&format=simplified&q=actionType=="DEPLOYED"'
        if app_id:
            ngsild_params += f'&q=service=="{app_id}"'
        aeros_apps = aeros_client.query_entities(ngsild_params)
        return [
            {
                "appInstanceId": service["id"],
                "status":
                # scomponent["serviceComponentStatus"].split(":")[-1].lower()
                service["actionType"],
            }
            for service in aeros_apps
        ]
        # return [{"appInstanceId": "abcd-efgh", "status": "ready"}]

    # def get_all_deployed_apps(self,
    #                           app_id: Optional[str] = None,
    #                           app_instance_id: Optional[str] = None,
    #                           region: Optional[str] = None) -> List[Dict]:
    #     # FIXME: Get services in deployed state
    #     aeros_client = ContinuumClient(self.base_url)
    #     ngsild_params = "type=ServiceComponent&format=simplified"
    #     if app_id:
    #         ngsild_params += f'&q=service=="{app_id}"'
    #     aeros_apps = aeros_client.query_entities(ngsild_params)
    #     return [{
    #         "appInstanceId":
    #         scomponent["id"],
    #         "status":
    #         scomponent["serviceComponentStatus"].split(":")[-1].lower()
    #     } for scomponent in aeros_apps]
    #     # return [{"appInstanceId": "abcd-efgh", "status": "ready"}]

    def undeploy_app(self, app_instance_id: str) -> None:
        # HLO-FE DELETE with app_id (service_id)
        aeros_client = ContinuumClient(self.base_url)
        _ = aeros_client.undeploy_service(app_instance_id)

    def get_edge_cloud_zones(
        self, region: Optional[str] = None, status: Optional[str] = None
    ) -> List[Dict]:
        aeros_client = ContinuumClient(self.base_url)
        ngsild_params = "type=Domain&format=simplified"
        aeros_domains = aeros_client.query_entities(ngsild_params)
        return [
            {
                "edgeCloudZoneId": domain["id"],
                "status": domain["domainStatus"].split(":")[-1].lower(),
            }
            for domain in aeros_domains
        ]

    # return [{"edgeCloudZoneId": "zone-1", "status": "active"}]

    def get_edge_cloud_zones_details(
        self, zone_id: str, flavour_id: Optional[str] = None
    ) -> Dict:
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
        ngsild_params = (
            f'format=simplified&type=InfrastructureElement&q=domain=="{zone_id}"'
        )
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
