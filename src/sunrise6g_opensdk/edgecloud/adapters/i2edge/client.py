# -*- coding: utf-8 -*-
##
# This file is part of the Open SDK
#
# Contributors:
#   - Adrián Pino Martínez (adrian.pino@i2cat.net)
#   - Sergio Giménez (sergio.gimenez@i2cat.net)
#   - César Cajas (cesar.cajas@i2cat.net)
##
from copy import deepcopy
from typing import Dict, List, Optional

from pydantic import ValidationError
from requests import Response

from sunrise6g_opensdk import logger
from sunrise6g_opensdk.edgecloud.core import schemas as camara_schemas
from sunrise6g_opensdk.edgecloud.core.edgecloud_interface import (
    EdgeCloudManagementInterface,
)
from sunrise6g_opensdk.edgecloud.core.utils import (
    build_custom_http_response,
)

from ...adapters.i2edge import schemas as i2edge_schemas
from .common import (
    I2EdgeError,
    i2edge_delete,
    i2edge_get,
    i2edge_post,
    i2edge_post_multiform_data,
)

log = logger.get_logger(__name__)


class EdgeApplicationManager(EdgeCloudManagementInterface):
    """
    i2Edge Client
    """

    def __init__(self, base_url: str, flavour_id: str):
        self.base_url = base_url
        self.flavour_id = flavour_id
        self.content_type_gsma = "application/json"
        self.encoding_gsma = "utf-8"

    # ====================================================================
    # CAMARA EDGE CLOUD MANAGEMENT API
    # ====================================================================

    # --------------------------------------------------------------------
    # Edge Cloud Zone Management (CAMARA)
    # --------------------------------------------------------------------

    def get_edge_cloud_zones(
        self, region: Optional[str] = None, status: Optional[str] = None
    ) -> Response:
        url = f"{self.base_url}/zones/list"
        params = {}

        try:
            response = i2edge_get(url, params=params)
            if response.status_code == 200:
                response.raise_for_status()
                i2edge_response = response.json()
                log.info("Availability zones retrieved successfully")
                # Normalise to CAMARA format
                camara_response = []
                for z in i2edge_response:
                    zone = camara_schemas.EdgeCloudZone(
                        # edgeCloudZoneId = camara_schemas.EdgeCloudZoneId(z["zoneId"]),
                        edgeCloudZoneId=camara_schemas.EdgeCloudZoneId(z["zoneId"]),
                        edgeCloudZoneName=camara_schemas.EdgeCloudZoneName(
                            z["nodeName"]
                        ),
                        edgeCloudProvider=camara_schemas.EdgeCloudProvider("i2edge"),
                        edgeCloudRegion=camara_schemas.EdgeCloudRegion(
                            z["geographyDetails"]
                        ),
                        edgeCloudZoneStatus=camara_schemas.EdgeCloudZoneStatus.unknown,
                    )
                    camara_response.append(zone)
                # Wrap into a Response object
                return build_custom_http_response(
                    status_code=response.status_code,
                    content=[zone.model_dump(mode="json") for zone in camara_response],
                    headers={"Content-Type": "application/json"},
                    encoding=response.encoding,
                    url=response.url,
                    request=response.request,
                )
            return response
        except KeyError as e:
            log.error(f"Missing required CAMARA field in app manifest: {e}")
            raise ValueError(f"Invalid CAMARA manifest – missing field: {e}")
        except I2EdgeError as e:
            log.error(f"Failed to retrieve edge cloud zones: {e}")
            raise

    # --------------------------------------------------------------------
    # Artefact Management (i2Edge-Specific, Non-CAMARA)
    # --------------------------------------------------------------------

    def create_artefact(
        self,
        artefact_id: str,
        artefact_name: str,
        repo_name: str,
        repo_type: str,
        repo_url: str,
        password: Optional[str] = None,
        token: Optional[str] = None,
        user_name: Optional[str] = None,
    ):
        repo_type = i2edge_schemas.RepoType(repo_type)
        url = "{}/artefact".format(self.base_url)
        payload = i2edge_schemas.ArtefactOnboarding(
            artefact_id=artefact_id,
            name=artefact_name,
            repo_password=password,
            repo_name=repo_name,
            repo_type=repo_type,
            repo_url=repo_url,
            repo_token=token,
            repo_user_name=user_name,
        )
        try:
            response = i2edge_post_multiform_data(url, payload)
            if response.status_code == 201:
                response.raise_for_status()
                log.info("Artifact added successfully")
                return response
            return response
        except I2EdgeError as e:
            raise e

    def get_artefact(self, artefact_id: str) -> Dict:
        url = "{}/artefact/{}".format(self.base_url, artefact_id)
        try:
            response = i2edge_get(url, artefact_id)
            if response.status_code == 200:
                response.raise_for_status()
                log.info("Artifact retrieved successfully")
                return response.json()
            return response
        except I2EdgeError as e:
            raise e

    def get_all_artefacts(self) -> List[Dict]:
        url = "{}/artefacts".format(self.base_url)
        try:
            response = i2edge_get(url, {})
            if response.status_code == 200:
                response.raise_for_status()
                log.info("Artifacts retrieved successfully")
                return response.json()
            return response
        except I2EdgeError as e:
            raise e

    def delete_artefact(self, artefact_id: str):
        url = "{}/artefact".format(self.base_url)
        try:
            response = i2edge_delete(url, artefact_id)
            if response.status_code == 200:
                response.raise_for_status()
                log.info("Artifact deleted successfully")
                return response
            return response
        except I2EdgeError as e:
            raise e

    # --------------------------------------------------------------------
    # Application Management (CAMARA-Compliant)
    # --------------------------------------------------------------------

    def onboard_app(self, app_manifest: Dict) -> Response:
        """
        Onboards an application using a CAMARA-compliant manifest.
        Translates the manifest to the i2Edge format and returns a CAMARA-compliant response.

        :param app_manifest: CAMARA-compliant application manifest
        :return: Response with status code, headers, and CAMARA-normalised payload
        """
        try:
            # Validate CAMARA input
            camara_schemas.AppManifest(**app_manifest)

            # Extract relevant fields from CAMARA manifest
            app_id = app_manifest["appId"]
            app_name = app_manifest["name"]
            app_version = app_manifest["version"]
            app_provider = app_manifest["appProvider"]

            # Map CAMARA to i2Edge
            artefact_id = app_id
            app_component_spec = i2edge_schemas.AppComponentSpec(artefactId=artefact_id)
            app_metadata = i2edge_schemas.AppMetaData(
                appName=app_name, appProviderId=app_provider, version=app_version
            )

            onboarding_data = i2edge_schemas.ApplicationOnboardingData(
                app_id=app_id,
                appProviderId=app_provider,
                appComponentSpecs=[app_component_spec],
                appMetaData=app_metadata,
            )

            i2edge_payload = i2edge_schemas.ApplicationOnboardingRequest(
                profile_data=onboarding_data
            )

            # Call i2Edge API
            i2edge_response = i2edge_post(
                f"{self.base_url}/application/onboarding",
                model_payload=i2edge_payload.model_dump(
                    mode="json", exclude_defaults=True
                ),
            )
            # OpenAPI specifies 201 for successful application onboarding
            if i2edge_response.status_code == 201:
                i2edge_response.raise_for_status()

                # Build CAMARA-compliant response using schema
                submitted_app = camara_schemas.SubmittedApp(
                    appId=camara_schemas.AppId(app_id)
                )

                log.info("App onboarded successfully")
                return build_custom_http_response(
                    status_code=i2edge_response.status_code,
                    content=submitted_app.model_dump(mode="json"),
                    headers={"Content-Type": "application/json"},
                    encoding="utf-8",
                    url=i2edge_response.url,
                    request=i2edge_response.request,
                )
            else:
                i2edge_response.raise_for_status()
        # TODO: Implement CAMARA-compliant error handling for failed onboarding responses
        except ValidationError as e:
            log.error(f"Invalid CAMARA manifest: {e}")
            raise ValueError(f"Invalid CAMARA manifest: {e}")
        except I2EdgeError as e:
            log.error(f"Failed to onboard app to i2Edge: {e}")
            raise

    def delete_onboarded_app(self, app_id: str) -> Response:
        """
        Deletes an onboarded application using CAMARA-compliant interface.
        Returns a CAMARA-compliant response.

        :param app_id: Unique identifier of the application
        :return: Response with status code, headers, and CAMARA-normalised payload
        """
        url = "{}/application/onboarding".format(self.base_url)
        try:
            response = i2edge_delete(url, app_id)
            response.raise_for_status()

            log.info("App onboarded deleted successfully")
            return build_custom_http_response(
                status_code=204,
                content="",
                headers={"Content-Type": "application/json"},
                encoding="utf-8",
                url=response.url,
                request=response.request,
            )
        except I2EdgeError as e:
            log.error(f"Failed to delete onboarded app from i2Edge: {e}")
            raise

    def get_onboarded_app(self, app_id: str) -> Response:
        """
        Retrieves information of a specific onboarded application using CAMARA-compliant interface.
        Returns a CAMARA-compliant response.

        :param app_id: Unique identifier of the application
        :return: Response with application details in CAMARA format
        """
        url = "{}/application/onboarding/{}".format(self.base_url, app_id)
        try:
            response = i2edge_get(url, app_id)
            response.raise_for_status()
            i2edge_response = response.json()

            # Extract and transform i2Edge response to CAMARA format
            profile_data = i2edge_response.get("profile_data", {})
            app_metadata = profile_data.get("appMetaData", {})

            # Build CAMARA-compliant response using schema
            # Note: This is a partial AppManifest for get operation
            app_manifest_response = {
                "appManifest": {
                    "appId": profile_data.get("app_id", app_id),
                    "name": app_metadata.get("appName", ""),
                    "version": app_metadata.get("version", ""),
                    "appProvider": profile_data.get("appProviderId", ""),
                    # Add other required fields with defaults if not available
                    "packageType": "CONTAINER",  # Default value
                    "appRepo": {"type": "PUBLICREPO", "imagePath": "not-available"},
                    "requiredResources": {
                        "infraKind": "kubernetes",
                        "applicationResources": {},
                        "isStandalone": False,
                    },
                    "componentSpec": [],
                }
            }

            log.info("App retrieved successfully")
            return build_custom_http_response(
                status_code=response.status_code,
                content=app_manifest_response,
                headers={"Content-Type": "application/json"},
                encoding="utf-8",
                url=response.url,
                request=response.request,
            )
        except I2EdgeError as e:
            log.error(f"Failed to retrieve onboarded app from i2Edge: {e}")
            raise

    def get_all_onboarded_apps(self) -> Response:
        """
        Retrieves a list of all onboarded applications using CAMARA-compliant interface.
        Returns a CAMARA-compliant response.

        :return: Response with list of application metadata in CAMARA format
        """
        url = "{}/applications/onboarding".format(self.base_url)
        params = {}
        try:
            response = i2edge_get(url, params)
            response.raise_for_status()
            i2edge_response = response.json()

            # Transform i2Edge response to CAMARA format using AppManifest schema
            camara_apps = []
            if isinstance(i2edge_response, list):
                for app_data in i2edge_response:
                    profile_data = app_data.get("profile_data", {})
                    app_metadata = profile_data.get("appMetaData", {})

                    # Build CAMARA AppManifest structure
                    app_manifest = camara_schemas.AppManifest(
                        appId=profile_data.get("app_id", ""),
                        name=app_metadata.get("appName", ""),
                        version=app_metadata.get("version", ""),
                        appProvider=profile_data.get("appProviderId", ""),
                        packageType="CONTAINER",
                        appRepo={"type": "PUBLICREPO", "imagePath": "not-available"},
                        requiredResources={
                            "infraKind": "kubernetes",
                            "applicationResources": {},
                            "isStandalone": False,
                        },
                        componentSpec=[],
                    )
                    camara_apps.append(app_manifest.model_dump(mode="json"))

            log.info("All onboarded apps retrieved successfully")
            return build_custom_http_response(
                status_code=response.status_code,
                content=camara_apps,
                headers={"Content-Type": "application/json"},
                encoding="utf-8",
                url=response.url,
                request=response.request,
            )
        except I2EdgeError as e:
            log.error(f"Failed to retrieve all onboarded apps from i2Edge: {e}")
            raise

    # def _select_best_flavour_for_app(self, zone_id) -> str:
    #     # list_of_flavours = self.get_edge_cloud_zones_details(zone_id)
    #     # <logic that select the best flavour>
    #     return flavourId

    def deploy_app(self, app_id: str, app_zones: List[Dict]) -> Response:
        """
        Deploys an application using CAMARA-compliant interface.
        Returns a CAMARA-compliant response with deployment details.

        :param app_id: Unique identifier of the application
        :param app_zones: List of Edge Cloud Zones where the app should be deployed
        :return: Response with deployment details in CAMARA format
        """
        appId = app_id

        # Get onboarded app metadata for deployment
        app_url = "{}/application/onboarding/{}".format(self.base_url, appId)
        try:
            app_response = i2edge_get(app_url, appId)
            app_response.raise_for_status()
            app_data = app_response.json()
        except I2EdgeError as e:
            log.error(f"Failed to retrieve app data for deployment: {e}")
            raise

        # Extract deployment parameters from app metadata and zones
        profile_data = app_data["profile_data"]
        appProviderId = profile_data["appProviderId"]
        appVersion = profile_data["appMetaData"]["version"]
        zone_info = app_zones[0]["EdgeCloudZone"]
        zone_id = zone_info["edgeCloudZoneId"]
        # flavourId = self._select_best_flavour_for_app(zone_id=zone_id)

        # Build deployment payload
        app_deploy_data = i2edge_schemas.AppDeployData(
            appId=appId,
            appProviderId=appProviderId,
            appVersion=appVersion,
            zoneInfo=i2edge_schemas.ZoneInfo(flavourId=self.flavour_id, zoneId=zone_id),
        )
        url = "{}/application_instance".format(self.base_url)
        payload = i2edge_schemas.AppDeploy(
            app_deploy_data=app_deploy_data, app_parameters={"namespace": "test"}
        )

        # Deployment request to i2Edge
        try:
            i2edge_response = i2edge_post(url, payload)
            if i2edge_response.status_code == 202:
                i2edge_response.raise_for_status()
                i2edge_data = i2edge_response.json()

                # Build CAMARA-compliant response
                app_instance_id = i2edge_data.get("app_instance_id")

                app_instance_info = camara_schemas.AppInstanceInfo(
                    name=camara_schemas.AppInstanceName(app_instance_id),
                    appId=camara_schemas.AppId(appId),
                    appInstanceId=camara_schemas.AppInstanceId(app_instance_id),
                    appProvider=camara_schemas.AppProvider(appProviderId),
                    status=camara_schemas.Status.instantiating,  # 202 means deployment is in progress
                    edgeCloudZoneId=camara_schemas.EdgeCloudZoneId(zone_id),
                )

                # CAMARA spec requires appInstances array wrapper
                camara_response = {
                    "appInstances": [app_instance_info.model_dump(mode="json")]
                }

                log.info("App deployment request submitted successfully")
                return build_custom_http_response(
                    status_code=i2edge_response.status_code,
                    content=camara_response,
                    headers={"Content-Type": "application/json"},
                    encoding="utf-8",
                    url=i2edge_response.url,
                    request=i2edge_response.request,
                )
            else:
                i2edge_response.raise_for_status()
        except I2EdgeError as e:
            log.error(f"Failed to deploy app to i2Edge: {e}")
            raise

    def get_all_deployed_apps(self) -> List[Dict]:
        url = "{}/application_instances".format(self.base_url)
        params = {}
        try:
            response = i2edge_get(url, params=params)
            if response.status_code == 200:
                response.raise_for_status()
                log.info("All app instances retrieved successfully")
                return response.json()
            return response
        except I2EdgeError as e:
            raise e

    def get_deployed_app(self, app_id, zone_id) -> List[Dict]:
        # Logic: Get all onboarded apps and filter the one where release_name == artifact name

        # Step 1) Extract "app_name" from the onboarded app using the "app_id"
        try:
            onboarded_app_response = self.get_onboarded_app(app_id)
            onboarded_app_response.raise_for_status()
            onboarded_app_data = onboarded_app_response.json()
        except I2EdgeError as e:
            log.error(f"Failed to retrieve app data: {e}")
            raise ValueError(f"No onboarded app found with ID: {app_id}")

        try:
            # Extract app name from CAMARA response format
            app_name = onboarded_app_data.get("name", "")
            if not app_name:
                raise KeyError("name")
        except KeyError as e:
            raise ValueError(f"Onboarded app missing required field: {e}")

        # Step 2) Retrieve all deployed apps and filter the one(s) where release_name == app_name
        deployed_apps = self.get_all_deployed_apps()
        if not deployed_apps:
            return []

        # Filter apps where release_name matches our app_name and zone matches
        for app_instance_name in deployed_apps:
            if (
                app_instance_name.get("release_name") == app_name
                and app_instance_name.get("zone_id") == zone_id
            ):
                return app_instance_name
        return None

    def undeploy_app(self, app_instance_id: str) -> Response:
        """
        Terminates a specific application instance using CAMARA-compliant interface.
        Returns a CAMARA-compliant response confirming termination.

        :param app_instance_id: Unique identifier of the application instance
        :return: Response confirming termination in CAMARA format (204 No Content)
        """
        url = "{}/application_instance".format(self.base_url)
        try:
            i2edge_response = i2edge_delete(url, app_instance_id)
            if i2edge_response.status_code == 200:
                i2edge_response.raise_for_status()

                log.info("App instance deleted successfully")
                # CAMARA-compliant 204 response (No Content for successful deletion)
                return build_custom_http_response(
                    status_code=204,
                    content="",
                    headers={"Content-Type": "application/json"},
                    encoding="utf-8",
                    url=i2edge_response.url,
                    request=i2edge_response.request,
                )
            else:
                i2edge_response.raise_for_status()
        except I2EdgeError as e:
            log.error(f"Failed to undeploy app from i2Edge: {e}")
            raise

    # ====================================================================
    # GSMA EDGE COMPUTING API (EWBI OPG) - FEDERATION
    # ====================================================================

    # --------------------------------------------------------------------
    # Federation Management (GSMA)
    # --------------------------------------------------------------------

    def get_edge_cloud_zones_list_gsma(self) -> List:
        url = "{}/zones/list".format(self.base_url)
        params = {}
        try:
            response = i2edge_get(url, params=params)
            if response.status_code == 200:
                response_json = response.json()
                response_list = []
                for item in response_json:
                    content = {
                        "zoneId": item.get("zoneId"),
                        "geolocation": item.get("geolocation"),
                        "geographyDetails": item.get("geographyDetails"),
                    }
                    response_list.append(content)
                return build_custom_http_response(
                    status_code=200,
                    content=response_list,
                    headers={"Content-Type": self.content_type_gsma},
                    encoding=self.encoding_gsma,
                    url=response.url,
                    request=response.request,
                )
            return response
        except I2EdgeError as e:
            raise e

    def get_edge_cloud_zones_gsma(self, federation_context_id: str) -> Dict:
        url = "{}/zones".format(self.base_url)
        params = {}
        try:
            response = i2edge_get(url, params=params)
            if response.status_code == 200:
                response_json = response.json()
                response_list = []
                for item in response_json:
                    content = {
                        "zoneId": item.get("zoneId"),
                        "reservedComputeResources": item.get(
                            "reservedComputeResources"
                        ),
                        "computeResourceQuotaLimits": item.get(
                            "computeResourceQuotaLimits"
                        ),
                        "flavoursSupported": item.get("flavoursSupported"),
                        "networkResources": item.get("networkResources"),
                        "zoneServiceLevelObjsInfo": item.get(
                            "zoneServiceLevelObjsInfo"
                        ),
                    }
                    response_list.append(content)
                return build_custom_http_response(
                    status_code=200,
                    content=response_list,
                    headers={"Content-Type": self.content_type_gsma},
                    encoding=self.encoding_gsma,
                    url=response.url,
                    request=response.request,
                )
            return response
        except I2EdgeError as e:
            raise e

    # --------------------------------------------------------------------
    # Availability Zone Info Synchronization (GSMA)
    # --------------------------------------------------------------------

    def availability_zone_info_gsma(
        self, federation_context_id: str, request_body: dict
    ) -> Dict:
        url = "{}/zones".format(self.base_url)
        params = {}
        try:
            response = i2edge_get(url, params=params)
            if response.status_code == 200:
                content = {"acceptedZoneResourceInfo": response.json()}
                return build_custom_http_response(
                    status_code=200,
                    content=content,
                    headers={"Content-Type": self.content_type_gsma},
                    encoding=self.encoding_gsma,
                    url=response.url,
                    request=response.request,
                )
            return response
        except I2EdgeError as e:
            raise e

    def get_edge_cloud_zone_details_gsma(
        self, federation_context_id: str, zone_id: str
    ) -> Dict:
        url = "{}/zone/{}".format(self.base_url, zone_id)
        params = {}
        try:
            response = i2edge_get(url, params=params)
            if response.status_code == 200:
                response_json = response.json()
                content = {
                    "zoneId": response_json.get("zoneID"),
                    "reservedComputeResources": response_json.get(
                        "reservedComputeResources"
                    ),
                    "computeResourceQuotaLimits": response_json.get(
                        "computeResourceQuotaLimits"
                    ),
                    "flavoursSupported": response_json.get("flavoursSupported"),
                    "networkResources": response_json.get("networkResources"),
                    "zoneServiceLevelObjsInfo": response_json.get(
                        "zoneServiceLevelObjsInfo"
                    ),
                }
                return build_custom_http_response(
                    status_code=200,
                    content=content,
                    headers={"Content-Type": self.content_type_gsma},
                    encoding=self.encoding_gsma,
                    url=response.url,
                    request=response.request,
                )
            return response
        except I2EdgeError as e:
            raise e

    # --------------------------------------------------------------------
    # Artefact Management (GSMA)
    # --------------------------------------------------------------------

    def create_artefact_gsma(
        self, federation_context_id: str, request_body: Dict
    ) -> Dict:
        try:
            artefact_id = request_body["artefactId"]
            artefact_name = request_body["artefactName"]
            repo_data = request_body["artefactRepoLocation"]

            transformed = {
                "artefact_id": artefact_id,
                "artefact_name": artefact_name,
                "repo_name": repo_data.get("repoName", "unknown-repo"),
                "repo_type": request_body.get("repoType", "PUBLICREPO"),
                "repo_url": repo_data["repoURL"],
                "user_name": repo_data.get("userName"),
                "password": repo_data.get("password"),
                "token": repo_data.get("token"),
            }

            response = self.create_artefact(**transformed)
            if response.status_code == 201:
                return build_custom_http_response(
                    status_code=200,
                    content={"response": "Artefact uploaded successfully"},
                    headers={"Content-Type": self.content_type_gsma},
                    encoding=self.encoding_gsma,
                    url=response.url,
                    request=response.request,
                )
            return response
        except KeyError as e:
            raise I2EdgeError(f"Missing required field in GSMA artefact payload: {e}")

    def get_artefact_gsma(self, federation_context_id: str, artefact_id: str) -> Dict:
        try:
            response = self.get_artefact(artefact_id)
            if response.status_code == 200:
                response_json = response.json()
                print(response_json)
                content = {
                    "artefactId": response_json.get("artefact_id"),
                    "appProviderId": "Ihs0gCqO65SHTz",
                    "artefactName": response_json.get("name"),
                    "artefactDescription": "string",
                    "artefactVersionInfo": response_json.get("version"),
                    "artefactVirtType": "VM_TYPE",
                    "artefactFileName": "stringst",
                    "artefactFileFormat": "ZIP",
                    "artefactDescriptorType": "HELM",
                    "repoType": response_json.get("repo_type"),
                    "artefactRepoLocation": {
                        "repoURL": response_json.get("repo_url"),
                        "userName": response_json.get("repo_user_name"),
                        "password": response_json.get("repo_password"),
                        "token": response_json.get("repo_token"),
                    },
                }
                return build_custom_http_response(
                    status_code=200,
                    content=content,
                    headers={"Content-Type": self.content_type_gsma},
                    encoding=self.encoding_gsma,
                    url=response.url,
                    request=response.request,
                )
            return response
        except KeyError as e:
            raise I2EdgeError(f"Missing artefactId in GSMA payload: {e}")

    def delete_artefact_gsma(self, federation_context_id: str, artefact_id: str):
        try:
            response = self.delete_artefact(artefact_id)
            if response.status_code == 200:
                return build_custom_http_response(
                    status_code=200,
                    content='{"response": "Artefact deletion successful"}',
                    headers={"Content-Type": self.content_type_gsma},
                    encoding=self.encoding_gsma,
                    url=response.url,
                    request=response.request,
                )
            return response
        except KeyError as e:
            raise I2EdgeError(f"Missing artefactId in GSMA payload: {e}")

    # --------------------------------------------------------------------
    # Application Onboarding Management (GSMA)
    # --------------------------------------------------------------------

    def onboard_app_gsma(
        self, federation_context_id: str, request_body: dict
    ) -> Response:
        body = deepcopy(request_body)
        try:
            body["app_id"] = body.pop("appId")
            body.pop("edgeAppFQDN", None)
            data = body
            payload = i2edge_schemas.ApplicationOnboardingRequest(profile_data=data)
            url = "{}/application/onboarding".format(self.base_url)
            response = i2edge_post(url, payload)
            if response.status_code == 200:
                return build_custom_http_response(
                    status_code=200,
                    content={"response": "Application onboarded successfully"},
                    headers={"Content-Type": self.content_type_gsma},
                    encoding=self.encoding_gsma,
                    url=response.url,
                    request=response.request,
                )
            return response
        except KeyError as e:
            raise I2EdgeError(f"Missing required field in GSMA onboarding payload: {e}")

    def get_onboarded_app_gsma(self, federation_context_id: str, app_id: str) -> Dict:
        try:
            response = self.get_onboarded_app(app_id)
            if response.status_code == 200:
                response_json = response.json()
                profile_data = response_json.get("profile_data")
                content = {
                    "appId": profile_data.get("app_id"),
                    "appProviderId": "string",
                    "appDeploymentZones": profile_data.get("appDeploymentZones"),
                    "appMetaData": profile_data.get("appMetadata"),
                    "appQoSProfile": profile_data.get("appQoSProfile"),
                    "appComponentSpecs": profile_data.get("appComponentSpecs"),
                }
                return build_custom_http_response(
                    status_code=200,
                    content=content,
                    headers={"Content-Type": self.content_type_gsma},
                    encoding=self.encoding_gsma,
                    url=response.url,
                    request=response.request,
                )
            return response
        except KeyError as e:
            raise I2EdgeError(f"Missing appId in GSMA payload: {e}")

    def patch_onboarded_app_gsma(
        self, federation_context_id: str, app_id: str, request_body: dict
    ) -> Dict:
        pass

    def delete_onboarded_app_gsma(self, federation_context_id: str, app_id: str):
        try:
            response = self.delete_onboarded_app(app_id)
            if response.status_code == 200:
                return build_custom_http_response(
                    status_code=200,
                    content={"response": "App deletion successful"},
                    headers={"Content-Type": self.content_type_gsma},
                    encoding=self.encoding_gsma,
                    url=response.url,
                    request=response.request,
                )
            return response
        except KeyError as e:
            raise I2EdgeError(f"Missing appId in GSMA payload: {e}")

    # --------------------------------------------------------------------
    # Application Deployment Management (GSMA)
    # --------------------------------------------------------------------

    def deploy_app_gsma(
        self, federation_context_id: str, idempotency_key: str, request_body: dict
    ):
        body = deepcopy(request_body)
        try:
            zone_id = body.get("zoneInfo").get("zoneId")
            flavour_id = body.get("zoneInfo").get("flavourId")
            app_deploy_data = i2edge_schemas.AppDeployData(
                appId=body.get("appId"),
                appProviderId=body.get("appProviderId"),
                appVersion=body.get("appVersion"),
                zoneInfo=i2edge_schemas.ZoneInfo(flavourId=flavour_id, zoneId=zone_id),
            )
            payload = i2edge_schemas.AppDeploy(
                app_deploy_data=app_deploy_data, app_parameters={"namespace": "test"}
            )
            url = "{}/application_instance".format(self.base_url)
            response = i2edge_post(url, payload)
            if response.status_code == 202:
                response_json = response.json()
                content = {
                    "zoneId": response_json.get("zoneID"),
                    "appInstIdentifier": response_json.get("app_instance_id"),
                }
                return build_custom_http_response(
                    status_code=202,
                    content=content,
                    headers={"Content-Type": self.content_type_gsma},
                    encoding=self.encoding_gsma,
                    url=response.url,
                    request=response.request,
                )
            return response
        except KeyError as e:
            raise I2EdgeError(f"Missing required field in GSMA deployment payload: {e}")

    def get_deployed_app_gsma(
        self,
        federation_context_id: str,
        app_id: str,
        app_instance_id: str,
        zone_id: str,
    ):
        try:
            url = "{}/application_instance/{}/{}".format(
                self.base_url, zone_id, app_instance_id
            )
            params = {}
            response = i2edge_get(url, params=params)
            if response.status_code == 200:
                response_json = response.json()
                content = {
                    "appInstanceState": response_json.get("appInstanceState"),
                    "accesspointInfo": response_json.get("accesspointInfo"),
                }
                return build_custom_http_response(
                    status_code=200,
                    content=content,
                    headers={"Content-Type": self.content_type_gsma},
                    encoding=self.encoding_gsma,
                    url=response.url,
                    request=response.request,
                )
            return response
        except KeyError as e:
            raise I2EdgeError(f"Missing appId or zoneId in GSMA payload: {e}")

    def get_all_deployed_apps_gsma(
        self,
        federation_context_id: str,
        app_id: str,
        app_provider: str,
    ):
        try:
            url = "{}/application_instances".format(self.base_url)
            params = {}
            response = i2edge_get(url, params=params)
            if response.status_code == 200:
                response_json = response.json()
                response_list = []
                for item in response_json:
                    content = [
                        {
                            "zoneId": item.get("app_spec")
                            .get("nodeSelector")
                            .get("feature.node.kubernetes.io/zoneID"),
                            "appInstanceInfo": [
                                {
                                    "appInstIdentifier": item.get("app_instance_id"),
                                    "appInstanceState": item.get("deploy_status"),
                                }
                            ],
                        }
                    ]
                    response_list.append(content)
                return build_custom_http_response(
                    status_code=200,
                    content=response_list,
                    headers={"Content-Type": self.content_type_gsma},
                    encoding=self.encoding_gsma,
                    url=response.url,
                    request=response.request,
                )
            return response
        except KeyError as e:
            raise I2EdgeError(f"Error retrieving apps: {e}")

    def undeploy_app_gsma(
        self,
        federation_context_id: str,
        app_id: str,
        app_instance_id: str,
        zone_id: str,
    ):
        try:
            url = "{}/application_instance".format(self.base_url)
            response = i2edge_delete(url, app_instance_id)
            if response.status_code == 200:
                return build_custom_http_response(
                    status_code=200,
                    content={
                        "response": "Application instance termination request accepted"
                    },
                    headers={"Content-Type": self.content_type_gsma},
                    encoding=self.encoding_gsma,
                    url=response.url,
                    request=response.request,
                )
            return response
        except KeyError as e:
            raise I2EdgeError(f"Missing appInstanceId in GSMA payload: {e}")
