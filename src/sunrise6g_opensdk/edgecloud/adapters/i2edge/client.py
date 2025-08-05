# -*- coding: utf-8 -*-
##
# This file is part of the Open SDK
#
# Contributors:
#   - Adrián Pino Martínez (adrian.pino@i2cat.net)
#   - Sergio Giménez (sergio.gimenez@i2cat.net)
#   - César Cajas (cesar.cajas@i2cat.net)
##
import json
from copy import deepcopy
from typing import Dict, List, Optional

from pydantic import ValidationError
from requests import Response

from sunrise6g_opensdk import logger
from sunrise6g_opensdk.edgecloud.core import gsma_schemas
from sunrise6g_opensdk.edgecloud.core import schemas as camara_schemas
from sunrise6g_opensdk.edgecloud.core.edgecloud_interface import (
    EdgeCloudManagementInterface,
)
from sunrise6g_opensdk.edgecloud.core.utils import build_custom_http_response

from ...adapters.i2edge import schemas as i2edge_schemas
from .common import (
    I2EdgeError,
    i2edge_delete,
    i2edge_get,
    i2edge_patch,
    i2edge_post,
    i2edge_post_multiform_data,
)
from .gsma_utils import map_zone

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

    def _transform_to_camara_zone(self, zone_data: dict) -> camara_schemas.EdgeCloudZone:
        """
        Transform i2Edge zone data to CAMARA EdgeCloudZone format.

        :param zone_data: Raw zone data from i2Edge API
        :return: CAMARA-compliant EdgeCloudZone object
        """
        return camara_schemas.EdgeCloudZone(
            edgeCloudZoneId=camara_schemas.EdgeCloudZoneId(zone_data.get("zoneId", "unknown")),
            edgeCloudZoneName=camara_schemas.EdgeCloudZoneName(
                zone_data.get("nodeName", "unknown")
            ),
            edgeCloudProvider=camara_schemas.EdgeCloudProvider("i2edge"),
            edgeCloudRegion=camara_schemas.EdgeCloudRegion(
                zone_data.get("geographyDetails", "unknown")
            ),
            edgeCloudZoneStatus=camara_schemas.EdgeCloudZoneStatus.unknown,
        )

    # ########################################################################
    # CAMARA EDGE CLOUD MANAGEMENT API
    # ########################################################################

    # ------------------------------------------------------------------------
    # Edge Cloud Zone Management (CAMARA)
    # ------------------------------------------------------------------------

    def get_edge_cloud_zones(
        self, region: Optional[str] = None, status: Optional[str] = None
    ) -> Response:
        """
        Retrieves a list of available Edge Cloud Zones.

        :param region: Filter by geographical region.
        :param status: Filter by status (active, inactive, unknown).
        :return: Response with list of Edge Cloud Zones in CAMARA format.
        """
        url = f"{self.base_url}/zones/list"
        params = {}

        try:
            response = i2edge_get(url, params=params)  # expects 200 by default
            i2edge_response = response.json()
            log.info("Availability zones retrieved successfully")
            # Normalise to CAMARA format
            camara_response = [self._transform_to_camara_zone(z) for z in i2edge_response]
            # Wrap into a Response object
            return build_custom_http_response(
                status_code=response.status_code,
                content=[zone.model_dump(mode="json") for zone in camara_response],
                headers={"Content-Type": "application/json"},
                encoding=response.encoding,
                url=response.url,
                request=response.request,
            )
        except KeyError as e:
            log.error(f"Missing required CAMARA field in app manifest: {e}")
            raise ValueError(f"Invalid CAMARA manifest – missing field: {e}")
        except I2EdgeError as e:
            log.error(f"Failed to retrieve edge cloud zones: {e}")
            raise

    # ------------------------------------------------------------------------
    # Artefact Management (i2Edge-Specific, Non-CAMARA)
    # ------------------------------------------------------------------------

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
    ) -> Response:
        """
        Creates an artefact in the i2Edge platform.
        This is an i2Edge-specific operation not covered by CAMARA standards.

        :param artefact_id: Unique identifier for the artefact
        :param artefact_name: Name of the artefact
        :param repo_name: Repository name
        :param repo_type: Type of repository (PUBLICREPO, PRIVATEREPO)
        :param repo_url: Repository URL
        :param password: Optional repository password
        :param token: Optional repository token
        :param user_name: Optional repository username
        :return: Response confirming artefact creation
        """
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

    def get_artefact(self, artefact_id: str) -> Response:
        """
        Retrieves details about a specific artefact.
        This is an i2Edge-specific operation not covered by CAMARA standards.

        :param artefact_id: Unique identifier of the artefact
        :return: Response with artefact details
        """
        url = "{}/artefact/{}".format(self.base_url, artefact_id)
        params = {}
        try:
            response = i2edge_get(url, params=params)
            log.info("Artifact retrieved successfully")
            return response
        except I2EdgeError as e:
            raise e

    def get_all_artefacts(self) -> Response:
        """
        Retrieves a list of all artefacts.
        This is an i2Edge-specific operation not covered by CAMARA standards.

        :return: Response with list of artefact details
        """
        url = "{}/artefact".format(self.base_url)
        params = {}
        try:
            response = i2edge_get(url, params=params)
            log.info("Artifacts retrieved successfully")
            return response
        except I2EdgeError as e:
            raise e

    def delete_artefact(self, artefact_id: str) -> Response:
        """
        Deletes a specific artefact from the i2Edge platform.
        This is an i2Edge-specific operation not covered by CAMARA standards.

        :param artefact_id: Unique identifier of the artefact to delete
        :return: Response confirming artefact deletion
        """
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

    # ------------------------------------------------------------------------
    # Application Management (CAMARA-Compliant)
    # ------------------------------------------------------------------------

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
                model_payload=i2edge_payload,
                expected_status=201,
            )
            # Build CAMARA-compliant response using schema
            submitted_app = camara_schemas.SubmittedApp(appId=camara_schemas.AppId(app_id))

            log.info("App onboarded successfully")
            return build_custom_http_response(
                status_code=i2edge_response.status_code,
                content=submitted_app.model_dump(mode="json"),
                headers={"Content-Type": "application/json"},
                encoding="utf-8",
                url=i2edge_response.url,
                request=i2edge_response.request,
            )
        except ValidationError as e:
            error_details = "; ".join(
                [f"Field '{err['loc'][0]}': {err['msg']}" for err in e.errors()]
            )
            log.error(f"Invalid CAMARA manifest: {error_details}")
            raise ValueError(f"Invalid CAMARA manifest: {error_details}")
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
            # i2Edge returns 200 for successful deletions, but CAMARA expects 204
            response = i2edge_delete(url, app_id, expected_status=200)
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
        params = {}
        try:
            response = i2edge_get(url, params=params)  # expects 200 by default
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
            response = i2edge_get(url, params=params)  # expects 200 by default
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
                        # Hardcoding mandatory fields that doesn't exist in i2Edge
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
            zoneInfo=i2edge_schemas.ZoneInfoRef(flavourId=self.flavour_id, zoneId=zone_id),
        )
        url = "{}/application_instance".format(self.base_url)
        payload = i2edge_schemas.AppDeploy(app_deploy_data=app_deploy_data)

        # Deployment request to i2Edge - CAMARA expects 202 for deployment
        try:
            i2edge_response = i2edge_post(url, payload, expected_status=202)
            i2edge_data = i2edge_response.json()

            # Build CAMARA-compliant response
            app_instance_id = i2edge_data.get("app_instance_id")

            app_instance_info = camara_schemas.AppInstanceInfo(
                name=camara_schemas.AppInstanceName(app_instance_id),
                appId=camara_schemas.AppId(appId),
                appInstanceId=camara_schemas.AppInstanceId(app_instance_id),
                appProvider=camara_schemas.AppProvider(appProviderId),
                status=camara_schemas.Status.instantiating,
                edgeCloudZoneId=camara_schemas.EdgeCloudZoneId(zone_id),
            )

            # CAMARA spec requires appInstances array wrapper
            camara_response = app_instance_info.model_dump(mode="json")

            # Add mandatory Location header
            location_url = f"/appinstances/{app_instance_id}"
            camara_headers = {"Content-Type": "application/json", "Location": location_url}

            log.info("App deployment request submitted successfully")
            return build_custom_http_response(
                status_code=i2edge_response.status_code,
                content=camara_response,
                headers=camara_headers,
                encoding="utf-8",
                url=i2edge_response.url,
                request=i2edge_response.request,
            )
        except I2EdgeError as e:
            log.error(f"Failed to deploy app to i2Edge: {e}")
            raise

    def get_all_deployed_apps(
        self,
        app_id: Optional[str] = None,
        app_instance_id: Optional[str] = None,
        region: Optional[str] = None,
    ) -> Response:
        """
        Retrieves information of all application instances using CAMARA-compliant interface.
        Returns a CAMARA-compliant response.

        :param app_id: Filter by application ID
        :param app_instance_id: Filter by instance ID
        :param region: Filter by Edge Cloud region
        :return: Response with application instance details in CAMARA format
        """
        url = "{}/application_instances".format(self.base_url)
        params = {}
        try:
            response = i2edge_get(url, params=params, expected_status=200)
            i2edge_response = response.json()

            # Transform i2Edge response to CAMARA format
            camara_instances = []
            if isinstance(i2edge_response, list):
                for instance_data in i2edge_response:
                    # Apply filters if provided
                    if app_id and instance_data.get("app_id") != app_id:
                        continue
                    if app_instance_id and instance_data.get("app_instance_id") != app_instance_id:
                        continue
                    if region and instance_data.get("region") != region:
                        continue

                    # Transform to CAMARA AppInstanceInfo
                    try:
                        # Map i2Edge status to CAMARA status
                        i2edge_status = instance_data.get("deploy_status", "unknown")
                        camara_status = "ready" if i2edge_status == "DEPLOYED" else "unknown"

                        # Extract zone_id from app_spec.nodeSelector
                        zone_id = "unknown"
                        app_spec = instance_data.get("app_spec", {})
                        node_selector = app_spec.get("nodeSelector", {})
                        if "feature.node.kubernetes.io/zoneID" in node_selector:
                            zone_id = node_selector["feature.node.kubernetes.io/zoneID"]

                        app_instance_info = camara_schemas.AppInstanceInfo(
                            name=camara_schemas.AppInstanceName(
                                instance_data.get("app_instance_id", "unknown")
                            ),
                            appId=camara_schemas.AppId(instance_data.get("app_id", "unknown")),
                            appInstanceId=camara_schemas.AppInstanceId(
                                instance_data.get("app_instance_id", "unknown")
                            ),
                            appProvider=camara_schemas.AppProvider(
                                instance_data.get("app_provider", "Unknown_Provider")
                            ),
                            status=camara_schemas.Status(
                                camara_status
                            ),  # FIX: Map DEPLOYED -> ready
                            edgeCloudZoneId=camara_schemas.EdgeCloudZoneId(
                                zone_id
                            ),  # FIX: Extract from nodeSelector
                        )
                        camara_instances.append(app_instance_info.model_dump(mode="json"))
                    except Exception as validation_error:
                        # Skip instances that fail validation
                        log.warning(f"Skipping invalid instance data: {validation_error}")
                        continue

            # CAMARA spec format for multiple instances response
            camara_response = {"appInstances": camara_instances}

            log.info("All app instances retrieved successfully")
            return build_custom_http_response(
                status_code=response.status_code,
                content=camara_response,
                headers={"Content-Type": "application/json"},
                encoding="utf-8",
                url=response.url,
                request=response.request,
            )
        except I2EdgeError as e:
            log.error(f"Failed to retrieve all app instances from i2Edge: {e}")
            raise

    def get_deployed_app(
        self, app_instance_id: str, app_id: Optional[str] = None, region: Optional[str] = None
    ) -> Response:
        """
        Retrieves information of a specific application instance using CAMARA-compliant interface.
        Returns a CAMARA-compliant response.

        :param app_instance_id: Unique identifier of the application instance (mandatory)
        :param app_id: Optional filter by application ID for validation
        :param region: Optional filter by Edge Cloud region for validation
        :return: Response with application instance details in CAMARA format
        """
        try:
            # Get raw i2Edge data without CAMARA filtering to find the zone_id
            url = "{}/application_instances".format(self.base_url)
            raw_response = i2edge_get(url, params={}, expected_status=200)
            raw_instances = raw_response.json()

            # Find the specific instance in raw data to get its zone_id
            target_zone_id = None
            original_instance = None
            if isinstance(raw_instances, list):
                for instance_data in raw_instances:
                    if instance_data.get("app_instance_id") == app_instance_id:
                        # Optional validation: check app_id if provided
                        if app_id and instance_data.get("app_id") != app_id:
                            log.warning(
                                f"App instance {app_instance_id} found but app_id mismatch: expected {app_id}, found {instance_data.get('app_id')}"
                            )
                            continue

                        # Optional validation: check region if provided
                        if region and instance_data.get("region") != region:
                            log.warning(
                                f"App instance {app_instance_id} found but region mismatch: expected {region}, found {instance_data.get('region')}"
                            )
                            continue

                        target_zone_id = instance_data.get("zone_id")
                        original_instance = instance_data
                        break

            # If instance not found in list, try to get a fallback zone dynamically
            if not target_zone_id:
                log.warning(
                    f"App instance {app_instance_id} not found in instances list, attempting to find fallback zone"
                )

                # Try to get available zones and use the first one as fallback
                try:
                    zones_response = self.get_edge_cloud_zones()
                    if zones_response.status_code == 200:
                        zones_data = (
                            zones_response.json()
                            if hasattr(zones_response, "json")
                            else json.loads(zones_response.content.decode())
                        )
                        if zones_data and len(zones_data) > 0:
                            target_zone_id = zones_data[0].get("edgeCloudZoneId")
                            log.info(f"Using fallback zone: {target_zone_id}")
                        else:
                            raise I2EdgeError("No available zones found for fallback")
                    else:
                        raise I2EdgeError(
                            f"Failed to retrieve zones for fallback: {zones_response.status_code}"
                        )
                except Exception as zone_error:
                    log.error(f"Could not retrieve fallback zone: {zone_error}")
                    raise I2EdgeError(
                        f"App instance {app_instance_id} not found and no fallback zone available"
                    )

                # Use provided app_id if available, otherwise mark as unknown since we don't have instance data
                fallback_app_id = app_id if app_id else "unknown"
                original_instance = {"app_id": fallback_app_id, "app_provider": "Unknown_Provider"}

            # Now use the correct i2Edge endpoint with zone_id and app_instance_id
            url = f"{self.base_url}/application_instance/{target_zone_id}/{app_instance_id}"
            params = {}
            response = i2edge_get(url, params=params, expected_status=200)
            i2edge_response = response.json()

            # The i2Edge response has different structure: {"accesspointInfo": [...], "appInstanceState": "DEPLOYED"}
            # We need to map this to CAMARA format and get additional info from the raw instance data

            # Transform i2Edge response to CAMARA format
            app_instance_info = camara_schemas.AppInstanceInfo(
                name=camara_schemas.AppInstanceName(app_instance_id),
                appId=camara_schemas.AppId(
                    original_instance.get("app_id") if original_instance else "unknown"
                ),
                appInstanceId=camara_schemas.AppInstanceId(app_instance_id),
                appProvider=camara_schemas.AppProvider(
                    original_instance.get("app_provider", "Unknown_Provider")
                    if original_instance
                    else "Unknown_Provider"
                ),
                status=camara_schemas.Status(
                    "ready" if i2edge_response.get("appInstanceState") == "DEPLOYED" else "unknown"
                ),
                edgeCloudZoneId=camara_schemas.EdgeCloudZoneId(target_zone_id),
            )

            # CAMARA spec format for single instance response
            camara_response = {"appInstance": app_instance_info.model_dump(mode="json")}

            log.info("App instance retrieved successfully")
            return build_custom_http_response(
                status_code=response.status_code,
                content=camara_response,
                headers={"Content-Type": "application/json"},
                encoding="utf-8",
                url=response.url,
                request=response.request,
            )
        except I2EdgeError as e:
            log.error(
                f"Failed to retrieve app instance from i2Edge (zone_id: {target_zone_id}): {e}"
            )
            raise

    def undeploy_app(self, app_instance_id: str) -> Response:
        """
        Terminates a specific application instance using CAMARA-compliant interface.
        Returns a CAMARA-compliant response confirming termination.

        :param app_instance_id: Unique identifier of the application instance
        :return: Response confirming termination in CAMARA format (204 No Content)
        """
        url = "{}/application_instance".format(self.base_url)
        try:
            # i2Edge returns 200 for successful deletions, but CAMARA expects 204
            i2edge_response = i2edge_delete(url, app_instance_id, expected_status=200)

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
        except I2EdgeError as e:
            log.error(f"Failed to undeploy app from i2Edge: {e}")
            raise

    # ########################################################################
    # GSMA EDGE COMPUTING API (EWBI OPG) - FEDERATION
    # ########################################################################

    # ------------------------------------------------------------------------
    # Zone Management (GSMA)
    # ------------------------------------------------------------------------

    def get_edge_cloud_zones_list_gsma(self) -> Response:
        """
        Retrieves details of all Zones for GSMA federation.

        :return: Response with zone details in GSMA format.
        """
        url = f"{self.base_url}/zones/list"
        params = {}
        try:
            response = i2edge_get(url, params=params, expected_status=200)
            response_json = response.json()
            try:
                validated_data = gsma_schemas.ZonesList.model_validate(response_json)
            except ValidationError as e:
                raise ValueError(f"Invalid schema: {e}")

            return build_custom_http_response(
                status_code=200,
                content=[zone.model_dump_json() for zone in validated_data.root],
                headers={"Content-Type": self.content_type_gsma},
                encoding=self.encoding_gsma,
                url=response.url,
                request=response.request,
            )
        except I2EdgeError as e:
            log.error(f"Failed to obtain Zones list from i2edge: {e}")
            raise

    def get_edge_cloud_zones_gsma(self) -> Response:
        """
        Retrieves details of all Zones with compute resources and flavours for GSMA federation.

        :return: Response with zones and detailed resource information.
        """
        url = f"{self.base_url}/zones"
        params = {}
        try:
            response = i2edge_get(url, params=params, expected_status=200)
            response_json = response.json()
            mapped = [map_zone(zone) for zone in response_json]
            try:
                validated_data = gsma_schemas.ZoneRegisteredDataList.model_validate(mapped)
            except ValidationError as e:
                raise ValueError(f"Invalid schema {e}")
            return build_custom_http_response(
                status_code=200,
                content=validated_data.model_dump_json(),
                headers={"Content-Type": self.content_type_gsma},
                encoding=self.encoding_gsma,
                url=response.url,
                request=response.request,
            )
        except I2EdgeError as e:
            log.error(f"Failed to obtain Zones details from i2edge: {e}")
            raise

    def get_edge_cloud_zone_details_gsma(self, zone_id: str) -> Response:
        """
        Retrieves details of a specific Edge Cloud Zone reserved
        for the specified zone by the partner OP using GSMA federation.

        :param zone_id: Unique identifier of the Edge Cloud Zone.
        :return: Response with Edge Cloud Zone details.
        """
        url = f"{self.base_url}/zone/{zone_id}"
        params = {}
        try:
            response = i2edge_get(url, params=params, expected_status=200)
            response_json = response.json()
            mapped = map_zone(response_json)
            try:
                validated_data = gsma_schemas.ZoneRegisteredData.model_validate(mapped)
            except ValidationError as e:
                raise ValueError(f"Invalid schema: {e}")
            return build_custom_http_response(
                status_code=200,
                content=validated_data.model_dump_json(),
                headers={"Content-Type": self.content_type_gsma},
                encoding=self.encoding_gsma,
                url=response.url,
                request=response.request,
            )
        except I2EdgeError as e:
            log.error(f"Failed to obtain Zones details from i2edge: {e}")
            raise

    # ------------------------------------------------------------------------
    # Artefact Management (GSMA)
    # ------------------------------------------------------------------------

    def create_artefact_gsma(self, request_body: Dict) -> Response:
        """
        Uploads application artefact on partner OP using GSMA federation.
        Artefact is a zip file containing scripts and/or packaging files like Terraform or Helm
        which are required to create an instance of an application.

        :param request_body: Payload with artefact information.
        :return: Response with artefact upload confirmation.
        """
        try:
            artefact_id = request_body["artefactId"]
            artefact_name = request_body["artefactName"]
            repo_data = request_body["artefactRepoLocation"]

            transformed = {
                "artefact_id": artefact_id,
                "artefact_name": artefact_name,
                "repo_name": repo_data.get("repoName"),
                "repo_type": request_body.get("repoType"),
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
        except I2EdgeError as e:
            log.error(f"Failed to create artefact: {e}")
            raise

    def get_artefact_gsma(self, artefact_id: str) -> Response:
        """
        Retrieves details about an artefact from partner OP using GSMA federation.

        :param artefact_id: Unique identifier of the artefact.
        :return: Response with artefact details.
        """
        try:
            response = self.get_artefact(artefact_id)
            if response.status_code == 200:
                response_json = response.json()
                content = gsma_schemas.Artefact(
                    artefactId=response_json.get("artefact_id"),
                    appProviderId=response_json.get("id"),
                    artefactName=response_json.get("name"),
                    artefactDescription="Description",
                    artefactVersionInfo=response_json.get("version"),
                    artefactVirtType="VM_TYPE",
                    artefactFileName="FileName",
                    artefactFileFormat="TAR",
                    artefactDescriptorType="HELM",
                    repoType=response_json.get("repo_type"),
                    artefactRepoLocation=gsma_schemas.ArtefactRepoLocation(
                        repoURL=response_json.get("repo_url"),
                        userName=response_json.get("repo_user_name"),
                        password=response_json.get("repo_password"),
                        token=response_json.get("repo_token"),
                    ),
                )
                try:
                    validated_data = gsma_schemas.Artefact.model_validate(content)
                except ValidationError as e:
                    raise ValueError(f"Invalid schema: {e}")
                return build_custom_http_response(
                    status_code=200,
                    content=validated_data.model_dump_json(),
                    headers={"Content-Type": self.content_type_gsma},
                    encoding=self.encoding_gsma,
                    url=response.url,
                    request=response.request,
                )
            return response
        except I2EdgeError as e:
            log.error(f"Failed to retrieve artefact: {e}")
            raise

    def delete_artefact_gsma(self, artefact_id: str) -> Response:
        """
        Removes an artefact from partners OP.

        :param artefact_id: Unique identifier of the artefact.
        :return: Response with artefact deletion confirmation.
        """
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

    # ------------------------------------------------------------------------
    # Application Onboarding Management (GSMA)
    # ------------------------------------------------------------------------

    def onboard_app_gsma(self, request_body: dict) -> Response:
        """
        Submits an application details to a partner OP.
        Based on the details provided, partner OP shall do bookkeeping,
        resource validation and other pre-deployment operations.

        :param request_body: Payload with onboarding info.
        :return: Response with onboarding confirmation.
        """
        body = deepcopy(request_body)
        try:
            body["app_id"] = body.pop("appId")
            body.pop("edgeAppFQDN", None)
            data = body
            payload = i2edge_schemas.ApplicationOnboardingRequest(profile_data=data)
            url = "{}/application/onboarding".format(self.base_url)
            response = i2edge_post(url, payload, expected_status=201)
            return build_custom_http_response(
                status_code=200,
                content={"response": "Application onboarded successfully"},
                headers={"Content-Type": self.content_type_gsma},
                encoding=self.encoding_gsma,
                url=response.url,
                request=response.request,
            )
        except I2EdgeError as e:
            log.error(f"Failed to onboard app: {e}")
            raise

    def get_onboarded_app_gsma(self, app_id: str) -> Response:
        """
        Retrieves application details from partner OP using GSMA federation.

        :param app_id: Identifier of the application onboarded.
        :return: Response with application details.
        """
        url = f"{self.base_url}/application/onboarding/{app_id}"
        params = {}
        try:
            response = i2edge_get(url, params, expected_status=200)
            response_json = response.json()
            profile_data = response_json.get("profile_data")
            app_deployment_zones = profile_data.get("appDeploymentZones")
            app_metadata = profile_data.get("appMetaData")
            app_qos_profile = profile_data.get("appQoSProfile")
            app_component_specs = profile_data.get("appComponentSpecs")
            content = gsma_schemas.ApplicationModel(
                appId=profile_data.get("app_id"),
                appProviderId="from_FM",
                appDeploymentZones=[
                    gsma_schemas.AppDeploymentZone(countryCode="ES", zoneInfo=zone_id)
                    for zone_id in app_deployment_zones
                ],
                appMetaData=gsma_schemas.AppMetaData(
                    appName=app_metadata.get("appName"),
                    version=app_metadata.get("version"),
                    appDescription=app_metadata.get("appDescription"),
                    mobilitySupport=app_metadata.get("mobilitySupport"),
                    accessToken=app_metadata.get("accessToken"),
                    category=app_metadata.get("category"),
                ),
                appQoSProfile=gsma_schemas.AppQoSProfile(
                    latencyConstraints=app_qos_profile.get("latencyConstraints"),
                    bandwidthRequired=app_qos_profile.get("bandwidthRequired"),
                    multiUserClients=app_qos_profile.get("multiUserClients"),
                    noOfUsersPerAppInst=app_qos_profile.get("noOfUsersPerAppInst"),
                    appProvisioning=app_qos_profile.get("appProvisioning"),
                ),
                appComponentSpecs=[
                    gsma_schemas.AppComponentSpec(**component) for component in app_component_specs
                ],
                onboardStatusInfo="ONBOARDED",
            )
            try:
                validated_data = gsma_schemas.ApplicationModel.model_validate(content)
            except ValidationError as e:
                raise ValueError(f"Invalid schema: {e}")
            return build_custom_http_response(
                status_code=200,
                content=validated_data.model_dump_json(),
                headers={"Content-Type": self.content_type_gsma},
                encoding=self.encoding_gsma,
                url=response.url,
                request=response.request,
            )
        except I2EdgeError as e:
            log.error(f"Failed to get onboarded app: {e}")
            raise

    def patch_onboarded_app_gsma(self, app_id: str, request_body: dict) -> Response:
        """
        Updates partner OP about changes in application compute resource requirements,
        QOS Profile, associated descriptor or change in associated components using GSMA federation.

        :param app_id: Identifier of the application onboarded.
        :param request_body: Payload with updated onboarding info.
        :return: Response with update confirmation.
        """
        url = f"{self.base_url}/application/onboarding/{app_id}"
        params = {}
        response = i2edge_get(url, params, expected_status=200)
        response_json = response.json()
        app_component_specs = request_body.get("appComponents")
        app_qos_profile = request_body.get("appUpdQoSProfile")
        response_json["profile_data"]["appQoSProfile"] = app_qos_profile
        response_json["profile_data"]["appComponentSpecs"] = app_component_specs
        data = response_json.get("profile_data")
        try:
            payload = i2edge_schemas.ApplicationOnboardingRequest(profile_data=data)
            url = "{}/application/onboarding/{}".format(self.base_url, app_id)
            response = i2edge_patch(url, payload, expected_status=200)
            return build_custom_http_response(
                status_code=200,
                content={"response": "Application update successful"},
                headers={"Content-Type": self.content_type_gsma},
                encoding=self.encoding_gsma,
                url=response.url,
                request=response.request,
            )
        except I2EdgeError as e:
            log.error(f"Failed to patch onboarded app: {e}")
            raise

    def delete_onboarded_app_gsma(self, app_id: str) -> Response:
        """
        Deboards an application from specific partner OP zones using GSMA federation.

        :param app_id: Identifier of the application onboarded.
        :return: Response with deboarding confirmation.
        """
        try:
            response = self.delete_onboarded_app(app_id)
            if response.status_code == 204:
                return build_custom_http_response(
                    status_code=200,
                    content={"response": "App deletion successful"},
                    headers={"Content-Type": self.content_type_gsma},
                    encoding=self.encoding_gsma,
                    url=response.url,
                    request=response.request,
                )
            return response
        except I2EdgeError as e:
            log.error(f"Failed to delete onboarded app: {e}")
            raise

    # ------------------------------------------------------------------------
    # Application Deployment Management (GSMA)
    # ------------------------------------------------------------------------

    def deploy_app_gsma(self, request_body: dict) -> Response:
        """
        Instantiates an application on a partner OP zone using GSMA federation.

        :param request_body: Payload with deployment information.
        :return: Response with deployment details.
        """
        body = deepcopy(request_body)
        try:
            zone_id = body.get("zoneInfo").get("zoneId")
            flavour_id = body.get("zoneInfo").get("flavourId")
            app_deploy_data = i2edge_schemas.AppDeployData(
                appId=body.get("appId"),
                appProviderId=body.get("appProviderId"),
                appVersion=body.get("appVersion"),
                zoneInfo=i2edge_schemas.ZoneInfoRef(flavourId=flavour_id, zoneId=zone_id),
            )
            payload = i2edge_schemas.AppDeploy(app_deploy_data=app_deploy_data)
            url = "{}/application_instance".format(self.base_url)
            response = i2edge_post(url, payload, expected_status=202)

            response_json = response.json()
            content = gsma_schemas.AppInstance(
                zoneId=response_json.get("zoneID"),
                appInstIdentifier=response_json.get("app_instance_id"),
            )
            try:
                validated_data = gsma_schemas.AppInstance.model_validate(content)
            except ValidationError as e:
                raise ValueError(f"Invalid schema: {e}")
            return build_custom_http_response(
                status_code=202,
                content=validated_data.model_dump_json(),
                headers={"Content-Type": self.content_type_gsma},
                encoding=self.encoding_gsma,
                url=response.url,
                request=response.request,
            )
        except I2EdgeError as e:
            log.error(f"Failed to deploy app: {e}")
            raise

    def get_deployed_app_gsma(self, app_id: str, app_instance_id: str, zone_id: str) -> Response:
        """
        Retrieves an application instance details from partner OP using GSMA federation.

        :param app_id: Identifier of the app.
        :param app_instance_id: Identifier of the deployed instance.
        :param zone_id: Identifier of the zone.
        :return: Response with application instance details.
        """
        try:
            url = "{}/application_instance/{}/{}".format(self.base_url, zone_id, app_instance_id)
            params = {}
            response = i2edge_get(url, params=params, expected_status=200)

            response_json = response.json()
            content = gsma_schemas.AppInstanceStatus(
                appInstanceState=response_json.get("appInstanceState"),
                accesspointInfo=response_json.get("accesspointInfo"),
            )
            try:
                validated_data = gsma_schemas.AppInstanceStatus.model_validate(content)
            except ValidationError as e:
                raise ValueError(f"Invalid schema: {e}")
            return build_custom_http_response(
                status_code=200,
                content=validated_data.model_dump_json(),
                headers={"Content-Type": self.content_type_gsma},
                encoding=self.encoding_gsma,
                url=response.url,
                request=response.request,
            )

        except I2EdgeError as e:
            log.error(f"Failed to retrieve deployed app: {e}")
            raise

    def get_all_deployed_apps_gsma(self) -> Response:
        """
        Retrieves all instances for a given application of partner OP using GSMA federation.

        :param app_id: Identifier of the app.
        :param app_provider: App provider identifier.
        :return: Response with application instances details.
        """
        try:
            url = "{}/application_instances".format(self.base_url)
            params = {}
            response = i2edge_get(url, params=params, expected_status=200)
            response_json = response.json()
            response_list = []
            for item in response_json:
                content = {
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

                response_list.append(content)
            try:
                validated_data = gsma_schemas.ZoneIdentifierList.model_validate(response_list)
            except ValidationError as e:
                raise ValueError(f"Invalid schema: {e}")
            return build_custom_http_response(
                status_code=200,
                content=validated_data.model_dump_json(),
                headers={"Content-Type": self.content_type_gsma},
                encoding=self.encoding_gsma,
                url=response.url,
                request=response.request,
            )
        except I2EdgeError as e:
            log.error(f"Failed to retrieve apps: {e}")
            raise

    def undeploy_app_gsma(self, app_id: str, app_instance_id: str, zone_id: str) -> Response:
        """
        Terminate an application instance on a partner OP zone.

        :param app_id: Identifier of the app.
        :param app_instance_id: Identifier of the deployed app.
        :param zone_id: Identifier of the zone.
        :return: Response with termination confirmation.
        """
        try:
            url = "{}/application_instance".format(self.base_url)
            response = i2edge_delete(url, app_instance_id, expected_status=200)
            return build_custom_http_response(
                status_code=200,
                content={"response": "Application instance termination request accepted"},
                headers={"Content-Type": self.content_type_gsma},
                encoding=self.encoding_gsma,
                url=response.url,
                request=response.request,
            )
        except I2EdgeError as e:
            log.error(f"Failed to delete app: {e}")
            raise
