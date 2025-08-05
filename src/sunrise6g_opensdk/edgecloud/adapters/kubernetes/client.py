# Mocked API for testing purposes
import logging
from typing import Dict, List, Optional

from kubernetes.client import V1Deployment
from requests import Response

from sunrise6g_opensdk.edgecloud.adapters.kubernetes.lib.core.piedge_encoder import (
    deploy_service_function,
)
from sunrise6g_opensdk.edgecloud.adapters.kubernetes.lib.models.app_manifest import (
    AppManifest,
)
from sunrise6g_opensdk.edgecloud.adapters.kubernetes.lib.models.deploy_service_function import (
    DeployServiceFunction,
)
from sunrise6g_opensdk.edgecloud.adapters.kubernetes.lib.models.service_function_registration_request import (
    ServiceFunctionRegistrationRequest,
)
from sunrise6g_opensdk.edgecloud.adapters.kubernetes.lib.utils.connector_db import (
    ConnectorDB,
)
from sunrise6g_opensdk.edgecloud.adapters.kubernetes.lib.utils.kubernetes_connector import (
    KubernetesConnector,
)
from sunrise6g_opensdk.edgecloud.core import schemas as camara_schemas
from sunrise6g_opensdk.edgecloud.core.edgecloud_interface import (
    EdgeCloudManagementInterface,
)
from sunrise6g_opensdk.edgecloud.core.utils import build_custom_http_response


class EdgeApplicationManager(EdgeCloudManagementInterface):

    def __init__(self, base_url: str, **kwargs):
        self.kubernetes_host = base_url
        self.edge_cloud_provider = kwargs.get("PLATFORM_PROVIDER")
        kubernetes_token = kwargs.get("KUBERNETES_MASTER_TOKEN")
        kubernetes_port = kwargs.get("KUBERNETES_MASTER_PORT")
        storage_uri = kwargs.get("EMP_STORAGE_URI")
        username = kwargs.get("KUBERNETES_USERNAME")
        namespace = kwargs.get("K8S_NAMESPACE")
        if base_url is not None and base_url != "":
            self.k8s_connector = KubernetesConnector(
                ip=self.kubernetes_host,
                port=kubernetes_port,
                token=kubernetes_token,
                username=username,
                namespace=namespace,
            )
        if storage_uri is not None:
            self.connector_db = ConnectorDB(storage_uri)

    def onboard_app(self, app_manifest: AppManifest) -> Response:
        print(f"Submitting application: {app_manifest}")
        logging.info("Extracting variables from payload...")

        app_id = app_manifest.get("appId")
        app_name = app_manifest.get("name")
        image = app_manifest.get("appRepo").get("imagePath")
        package_type = app_manifest.get("packageType")
        network_interfaces = app_manifest.get("componentSpec")[0].get("networkInterfaces")
        ports = []
        req_resources = app_manifest.get("requiredResources")
        version = app_manifest.get("version")
        app_provider = app_manifest.get("appProvider")
        for ni in network_interfaces:
            ports.append(ni.get("port"))
        insert_doc = ServiceFunctionRegistrationRequest(
            service_function_id=app_id,
            service_function_image=image,
            service_function_name=app_name,
            service_function_type=package_type,
            application_ports=ports,
            required_resources=req_resources,
            app_provider=app_provider,
            version=version,
        )
        result = self.connector_db.insert_document_service_function(insert_doc.to_dict())
        if type(result) is str:
            status_code = 409
            submitted_app = {"message": "App already exists"}
        else:
            submitted_app = camara_schemas.SubmittedApp(
                appId=camara_schemas.AppId(result.inserted_id)
            ).model_dump(mode="json")
            status_code = 201
        return build_custom_http_response(
            status_code=status_code,
            content=submitted_app,
            headers={"Content-Type": "application/json"},
            encoding="utf-8",
            url=None,
            request=None,
        )

    def get_all_onboarded_apps(self) -> Response:
        logging.info("Retrieving all registered apps from database...")
        status_code = None
        content = []
        try:
            db_list = self.connector_db.get_documents_from_collection(
                collection_input="service_functions"
            )

            for sf in db_list:
                content.append(self.__transform_to_camara(sf))
            status_code = 200
            return build_custom_http_response(
                status_code=status_code,
                content=content,
                headers={"Content-Type": "application/json"},
                encoding="utf-8",
                url=None,
                request=None,
            )
        except Exception as e:
            logging.error(e.args)
            status_code = 500
            return {
                "status": 500,
                "code": "INTERNAL",
                "message": "Internal server error: " + e.args,
            }

    def get_onboarded_app(self, app_id: str) -> Response:
        logging.info("Searching for registered app with ID: " + app_id + " in database...")
        status_code = None
        content = None
        app = self.connector_db.get_documents_from_collection(
            "service_functions", input_type="_id", input_value=app_id
        )
        if len(app) > 0:
            status_code = 200
            content = {"appManifest": self.__transform_to_camara(app[0])}

        else:
            status_code = 404
            content = {"status": 404, "code": "NOT_FOUND", "message": "Resource does not exist"}
        return build_custom_http_response(
            status_code=status_code,
            content=content,
            headers={"Content-Type": "application/json"},
            encoding="utf-8",
            url=None,
            request=None,
        )

    def delete_onboarded_app(self, app_id: str) -> Response:
        result, code = self.connector_db.delete_document_service_function(_id=app_id)
        print(f"Removing application metadata: {app_id}")
        if code == 200:
            status_code = 204
            content = None
        else:
            status_code = 404
            content = {"status": 404, "code": "NOT_FOUND", "message": "Resource does not exist"}
        return build_custom_http_response(
            status_code=status_code,
            content=content,
            headers={"Content-Type": "application/json"},
            encoding="utf-8",
            url=None,
            request=None,
        )

    def deploy_app(self, app_id: str, app_zones: List[Dict]) -> Response:
        logging.info("Searching for registered app with ID: " + app_id + " in database...")
        status_code = None
        app = self.connector_db.get_documents_from_collection(
            "service_functions", input_type="_id", input_value=app_id
        )
        # success_response = []
        result = None
        response = None
        if len(app) < 1:
            return "Application with ID: " + app_id + " not found", 404
        if app is not None:
            sf = DeployServiceFunction(
                service_function_name=app[0].get("name"),
                service_function_instance_name=app[0].get("name"),
                # service_function_instance_name=body.get("name"),
                # location=body.get('edgeCloudZoneId'),
            )
            result = deploy_service_function(
                service_function=sf,
                connector_db=self.connector_db,
                kubernetes_connector=self.k8s_connector,
            )

        if type(result) is V1Deployment:
            status_code = 202
            response = {}
            response["name"] = result.metadata.name
            response["appId"] = app[0].get("_id")
            response["appInstanceId"] = result.metadata.uid
            response["appProvider"] = app[0].get("app_provider")
            response["status"] = "unknown"
            # interfaces = []
            # for port in deployment.get("ports"):
            #     access_point = {"port": port}
            #     interfaces.append({"interfaceId": "", "accessPoints": access_point})
            # response["componentEndpointInfo"] = interfaces
            # FIXME: avoid harcoded values that assign fake ids
            response["kubernetesClusterRef"] = "642f6105-7015-4af1-a4d1-e1ecb8437abc"
            response["edgeCloudZoneId"] = app_zones[0].get("EdgeCloudZone").get("edgeCloudZoneId")

        elif "Conflict" in result:
            status_code = 409
            response = {
                "status": 409,
                "code": "CONFLICT",
                "message": "Application already instantiated in the given Edge Cloud Zone",
            }
        return build_custom_http_response(
            status_code=status_code,
            content=response,
            headers={"Content-Type": "application/json"},
            encoding="utf-8",
            url=None,
            request=None,
        )

    def get_all_deployed_apps(
        self,
        app_id: Optional[str] = None,
        app_instance_id: Optional[str] = None,
        region: Optional[str] = None,
    ) -> Response:
        logging.info("Retrieving all deployed apps in the edge cloud platform")
        status_code = None
        content = None
        try:
            deployments = self.k8s_connector.get_deployed_service_functions(self.connector_db)
            response = []
            for deployment in deployments:
                item = {}
                item["name"] = deployment.get("service_function_catalogue_name")
                item["appId"] = deployment.get("appId")
                item["appProvider"] = deployment.get("appProvider")
                item["appInstanceId"] = deployment.get("appInstanceId")
                item["status"] = deployment.get("status", "unknown")
                interfaces = []
                for port in deployment.get("ports"):
                    access_point = {"port": port}
                    interfaces.append({"interfaceId": "", "accessPoints": access_point})
                # item["componentEndpointInfo"] = interfaces
                # FIXME: avoid harcoded values that assign fake ids
                item["kubernetesClusterRef"] = "642f6105-7015-4af1-a4d1-e1ecb8437abc"
                item["edgeCloudZoneId"] = deployment.get(
                    "edgeCloudZoneId", "6824d63a-4d5b-4624-a487-dbdf118b0fdb"
                )
                response.append(item)
            content = {"appInstances": response}
            status_code = 200
            return build_custom_http_response(
                status_code=status_code,
                content=content,
                headers={"Content-Type": "application/json"},
                encoding="utf-8",
                url=None,
                request=None,
            )
        except Exception as e:
            logging.error(e.args)
            return {
                "status": 500,
                "code": "INTERNAL",
                "message": "Internal server error: " + e.args,
            }

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
        logging.info("Retrieving for deployed app with ID: " + app_instance_id)
        deployments = self.k8s_connector.get_deployed_service_functions(self.connector_db)
        deployed_app = None
        response = {}
        for deployment in deployments:
            if deployment.get("appInstanceId") == app_instance_id:
                deployed_app = deployment
                break
        if deployed_app is not None:
            status_code = 200
            response["name"] = deployed_app.get("service_function_catalogue_name")
            response["appId"] = deployed_app.get("appId")
            response["appProvider"] = deployed_app.get("appProvider")
            response["appInstanceId"] = deployed_app.get("appInstanceId")
            response["status"] = deployed_app.get("status", "unknown")
            interfaces = []
            for port in deployed_app.get("ports"):
                access_point = {"port": port}
                interfaces.append({"interfaceId": "", "accessPoints": access_point})
            # response["componentEndpointInfo"] = interfaces
            # FIXME: avoid harcoded values that assign fake ids
            response["kubernetesClusterRef"] = "642f6105-7015-4af1-a4d1-e1ecb8437abc"
            # FIXME: avoid harcoded values that assign fake ids
            response["edgeCloudZoneId"] = deployed_app.get(
                "edgeCloudZoneId", "6824d63a-4d5b-4624-a487-dbdf118b0fdb"
            )
            response = {"appInstance": response}
        else:
            status_code = 404
            response = {
                "status": 404,
                "code": "NOT_FOUND",
                "message": "App instance does not exist",
            }
        return build_custom_http_response(
            status_code=status_code,
            content=response,
            headers={"Content-Type": "application/json"},
            encoding="utf-8",
            url=None,
            request=None,
        )

    def undeploy_app(self, app_instance_id: str) -> None:
        logging.info("Searching for deployed app with ID: " + app_instance_id + " in database...")
        print(f"Deleting app instance: {app_instance_id}")
        status_code = 404
        try:
            sfs = self.k8s_connector.get_deployed_service_functions(self.connector_db)
            # response = "App instance with ID [" + app_instance_id + "] not found"
            for service_fun in sfs:
                if service_fun["appInstanceId"] == app_instance_id:
                    print(service_fun["service_function_instance_name"])
                    self.k8s_connector.delete_service_function(
                        self.connector_db, service_fun["service_function_instance_name"]
                    )

                    status_code = 204
                    break
            return build_custom_http_response(
                status_code=status_code,
                content=None,
                headers={"Content-Type": "application/json"},
                encoding="utf-8",
                url=None,
                request=None,
            )
        except Exception as e:
            logging.error(e.args)
            return {"status": 404, "code": "NOT_FOUND", "message": "Resource does not exist"}

    def get_edge_cloud_zones(
        self, region: Optional[str] = None, status: Optional[str] = None
    ) -> Response:

        nodes_response = self.k8s_connector.get_PoPs()
        zone_list = []

        for node in nodes_response:
            zone = {}
            zone["edgeCloudZoneId"] = node.get("uid")
            zone["edgeCloudZoneName"] = node.get("name")
            zone["edgeCloudZoneStatus"] = node.get("status")
            zone["edgeCloudProvider"] = self.edge_cloud_provider
            zone["edgeCloudRegion"] = node.get("location")
            zone_list.append(zone)
        logging.info(zone_list)
        return build_custom_http_response(
            status_code=200,
            content=zone_list,
            headers={"Content-Type": "application/json"},
            encoding="utf-8",
            url=None,
            request=None,
        )

    def get_edge_cloud_zones_details(
        self, zone_id: str, flavour_id: Optional[str] = None
    ) -> Response:
        nodes = self.k8s_connector.get_node_details()
        node_details = None
        for item in nodes.get("items"):
            # TODO: Fix uid stuff
            if item.get("metadata").get("uid") == zone_id:
                node_details = item
                break
        labels = node_details.get("metadata").get("labels")
        status = node_details.get("status")
        arch_type = labels.get("beta.kubernetes.io/arch")
        computeResourceQuotaLimits = [
            {
                "cpuArchType": arch_type,
                "numCPU": status.get("capacity").get("cpu"),
                "memory": status.get("capacity").get("memory"),
                # "memory": int(status.get("capacity").get("memory")) / (1024 * 1024),
            }
        ]
        reservedComputeResources = [
            {
                "cpuArchType": arch_type,
                "numCPU": status.get("allocatable").get("cpu"),
                "memory": status.get("allocatable").get("memory"),
                # "memory": int(status.get("allocatable").get("memory")) / (1024 * 1024),
            }
        ]
        flavoursSupported = []
        node_details["computeResourceQuotaLimits"] = computeResourceQuotaLimits
        node_details["reservedComputeResources"] = reservedComputeResources
        node_details["flavoursSupported"] = flavoursSupported
        node_details["zoneId"] = zone_id
        return build_custom_http_response(
            status_code=200,
            content=node_details,
            headers={"Content-Type": "application/json"},
            encoding="utf-8",
            url=None,
            request=None,
        )

    def __transform_to_camara(self, app_data):
        app = {}
        app["appId"] = app_data.get("_id")
        app["name"] = app_data.get("name")
        app["packageType"] = app_data.get("type")
        appRepo = {"imagePath": app_data.get("image"), "type": "PUBLICREPO"}
        app["appRepo"] = appRepo
        networkInterfaces = []
        for port in app_data.get("application_ports"):
            port_spec = {
                "protocol": "TCP",
                "port": port,
                "visibilityType": "VISIBILITY_EXTERNAL",
                # FIXME: avoid harcoded values that assign fake ids
                "interfaceId": "gUn3d3EKG05T0zWZynI5c1d9l9QE",
            }
            networkInterfaces.append(port_spec)
        app["componentSpec"] = [
            {
                "componentName": app_data.get("name"),
                "networkInterfaces": networkInterfaces,
            }
        ]
        app["appProvider"] = app_data.get("app_provider")
        app["requiredResources"] = app_data.get("required_resources")
        app["version"] = app_data.get("version")
        return app

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
