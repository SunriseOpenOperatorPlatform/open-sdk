# -*- coding: utf-8 -*-
##
# This file is part of the Open SDK
#
# Contributors:
#   - Adrián Pino Martínez (adrian.pino@i2cat.net)
#   - Sergio Giménez (sergio.gimenez@i2cat.net)
##
from typing import Dict, List, Optional

from sunrise6g_opensdk import logger
from sunrise6g_opensdk.edgecloud.core.edgecloud_interface import (
    EdgeCloudManagementInterface,
)

from ...adapters.i2edge import schemas
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

    def get_edge_cloud_zones(
        self, region: Optional[str] = None, status: Optional[str] = None
    ) -> list[dict]:
        url = "{}/zones/list".format(self.base_url)
        params = {}
        try:
            response = i2edge_get(url, params=params)
            log.info("Availability zones retrieved successfully")
            return response
        except I2EdgeError as e:
            raise e

    def get_edge_cloud_zones_details(
        self, zone_id: str, flavour_id: Optional[str] = None
    ) -> Dict:
        url = "{}zone/{}".format(self.base_url, zone_id)
        params = {}
        try:
            response = i2edge_get(url, params=params)
            log.info("Availability zone details retrieved successfully")
            return response
        except I2EdgeError as e:
            raise e

    def _create_artefact(
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
        repo_type = schemas.RepoType(repo_type)
        url = "{}/artefact".format(self.base_url)
        payload = schemas.ArtefactOnboarding(
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
            i2edge_post_multiform_data(url, payload)
            log.info("Artifact added successfully")
        except I2EdgeError as e:
            raise e

    def _get_artefact(self, artefact_id: str) -> Dict:
        url = "{}/artefact/{}".format(self.base_url, artefact_id)
        try:
            response = i2edge_get(url, artefact_id)
            log.info("Artifact retrieved successfully")
            return response
        except I2EdgeError as e:
            raise e

    def _get_all_artefacts(self) -> List[Dict]:
        url = "{}/artefact".format(self.base_url)
        try:
            response = i2edge_get(url, {})
            log.info("Artifacts retrieved successfully")
            return response
        except I2EdgeError as e:
            raise e

    def _delete_artefact(self, artefact_id: str):
        url = "{}/artefact".format(self.base_url)
        try:
            i2edge_delete(url, artefact_id)
            log.info("Artifact deleted successfully")
        except I2EdgeError as e:
            raise e

    def onboard_app(self, app_manifest: Dict) -> Dict:
        try:
            app_id = app_manifest["appId"]
            artefact_id = app_id

            app_component_spec = schemas.AppComponentSpec(artefactId=artefact_id)
            data = schemas.ApplicationOnboardingData(
                app_id=app_id, appComponentSpecs=[app_component_spec]
            )
            payload = schemas.ApplicationOnboardingRequest(profile_data=data)
            url = "{}/application/onboarding".format(self.base_url)
            i2edge_post(url, payload)
        except I2EdgeError as e:
            raise e
        except KeyError as e:
            raise I2EdgeError("Missing required field in app_manifest: {}".format(e))

    def delete_onboarded_app(self, app_id: str) -> None:
        url = "{}/application/onboarding".format(self.base_url)
        try:
            i2edge_delete(url, app_id)
        except I2EdgeError as e:
            raise e

    def get_onboarded_app(self, app_id: str) -> Dict:
        url = "{}/application/onboarding/{}".format(self.base_url, app_id)
        try:
            response = i2edge_get(url, app_id)
            return response
        except I2EdgeError as e:
            raise e

    def get_all_onboarded_apps(self) -> List[Dict]:
        url = "{}/applications/onboarding".format(self.base_url)
        params = {}
        try:
            response = i2edge_get(url, params)
            return response
        except I2EdgeError as e:
            raise e

    # def _select_best_flavour_for_app(self, zone_id) -> str:
    #     # list_of_flavours = self.get_edge_cloud_zones_details(zone_id)
    #     # <logic that select the best flavour>
    #     return flavourId

    def deploy_app(self, app_id: str, app_zones: List[Dict]) -> Dict:
        appId = app_id
        app = self.get_onboarded_app(appId)
        profile_data = app["profile_data"]
        appProviderId = profile_data["appProviderId"]
        appVersion = profile_data["appMetaData"]["version"]
        zone_info = app_zones[0]["EdgeCloudZone"]
        zone_id = zone_info["edgeCloudZoneId"]
        # TODO: atm the flavour id is specified as an input parameter
        # flavourId = self._select_best_flavour_for_app(zone_id=zone_id)
        app_deploy_data = schemas.AppDeployData(
            appId=appId,
            appProviderId=appProviderId,
            appVersion=appVersion,
            zoneInfo=schemas.ZoneInfo(flavourId=self.flavour_id, zoneId=zone_id),
        )
        url = "{}/app/".format(self.base_url)
        payload = schemas.AppDeploy(app_deploy_data=app_deploy_data)
        try:
            response = i2edge_post(url, payload)
            log.info("App deployed successfully")
            print(response)
            return response
        except I2EdgeError as e:
            raise e

    def get_all_deployed_apps(self) -> List[Dict]:
        url = "{}/app/".format(self.base_url)
        params = {}
        try:
            response = i2edge_get(url, params=params)
            log.info("All app instances retrieved successfully")
            return response
        except I2EdgeError as e:
            raise e

    def get_deployed_app(self, app_id, zone_id) -> List[Dict]:
        # Logic: Get all onboarded apps and filter the one where release_name == artifact name

        # Step 1) Extract "app_name" from the onboarded app using the "app_id"
        onboarded_app = self.get_onboarded_app(app_id)
        if not onboarded_app:
            raise ValueError(f"No onboarded app found with ID: {app_id}")

        try:
            app_name = onboarded_app["profile_data"]["appMetaData"]["appName"]
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

        url = "{}/app/{}/{}".format(self.base_url, zone_id, app_instance_name)
        params = {}
        try:
            response = i2edge_get(url, params=params)
            log.info("App instance retrieved successfully")
            return response
        except I2EdgeError as e:
            raise e

    def undeploy_app(self, app_instance_id: str) -> None:
        url = "{}/app".format(self.base_url)
        try:
            i2edge_delete(url, app_instance_id)
            log.info("App instance deleted successfully")
        except I2EdgeError as e:
            raise e
