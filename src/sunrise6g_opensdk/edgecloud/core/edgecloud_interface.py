#!/usr/bin/env python3
# -*- coding: utf-8 -*-
##
# This file is part of the Open SDK
#
# Contributors:
#   - Adrián Pino Martínez (adrian.pino@i2cat.net)
#   - César Cajas (cesar.cajas@i2cat.net)
##
from abc import ABC, abstractmethod
from typing import Dict, List, Optional


class EdgeCloudManagementInterface(ABC):
    """
    Abstract Base Class for Edge Application Management.
    """

    @abstractmethod
    def onboard_app(self, app_manifest: Dict) -> Dict:
        """
        Onboards an app, submitting application metadata
        to the Edge Cloud Provider.

        :param app_manifest: Application metadata in dictionary format.
        :return: Dictionary containing created application details.
        """
        pass

    @abstractmethod
    def get_all_onboarded_apps(self) -> List[Dict]:
        """
        Retrieves a list of onboarded applications.

        :return: List of application metadata dictionaries.
        """
        pass

    @abstractmethod
    def get_onboarded_app(self, app_id: str) -> Dict:
        """
        Retrieves information of a specific onboarded application.

        :param app_id: Unique identifier of the application.
        :return: Dictionary with application details.
        """
        pass

    @abstractmethod
    def delete_onboarded_app(self, app_id: str) -> None:
        """
        Deletes an application onboarded from the Edge Cloud Provider.

        :param app_id: Unique identifier of the application.
        """
        pass

    @abstractmethod
    def deploy_app(self, app_id: str, app_zones: List[Dict]) -> Dict:
        """
        Requests the instantiation of an application instance.

        :param app_id: Unique identifier of the application.
        :param app_zones: List of Edge Cloud Zones where the app should be
        instantiated.
        :return: Dictionary with instance details.
        """
        pass

    @abstractmethod
    def get_all_deployed_apps(
        self,
        app_id: Optional[str] = None,
        app_instance_id: Optional[str] = None,
        region: Optional[str] = None,
    ) -> List[Dict]:
        """
        Retrieves information of application instances.

        :param app_id: Filter by application ID.
        :param app_instance_id: Filter by instance ID.
        :param region: Filter by Edge Cloud region.
        :return: List of application instance details.
        """
        pass

    @abstractmethod
    def undeploy_app(self, app_instance_id: str) -> None:
        """
        Terminates a specific application instance.

        :param app_instance_id: Unique identifier of the application instance.
        """
        pass

    @abstractmethod
    def get_edge_cloud_zones(
        self, region: Optional[str] = None, status: Optional[str] = None
    ) -> List[Dict]:
        """
        Retrieves a list of available Edge Cloud Zones.

        :param region: Filter by geographical region.
        :param status: Filter by status (active, inactive, unknown).
        :return: List of Edge Cloud Zones.
        """
        pass

    @abstractmethod
    def get_edge_cloud_zones_details(
        self, federation_context_id: str, zone_id: str
    ) -> Dict:
        """
        Retrieves details of a specific Edge Cloud Zone reserved
        for the specified zone by the partner OP.

        :param federation_context_id: Identifier of the federation context.
        :param zone_id: Unique identifier of the Edge Cloud Zone.
        :return: Dictionary with Edge Cloud Zone details.
        """
        pass

    # --- GSMA-specific methods ---

    # FederationManagement

    @abstractmethod
    def get_edge_cloud_zones_list_gsma(self) -> List:
        """
        Retrieves list of all Zones

        :return: List.
        """
        pass

    # AvailabilityZoneInfoSynchronization

    @abstractmethod
    def get_edge_cloud_zones_gsma(self) -> List:
        """
        Retrieves details of all Zones

        :return: List.
        """
        pass

    @abstractmethod
    def get_edge_cloud_zone_details_gsma(self, zone_id: str) -> Dict:
        """
        Retrieves details of a specific Edge Cloud Zone reserved
        for the specified zone by the partner OP.

        :param zone_id: Unique identifier of the Edge Cloud Zone.
        :return: Dictionary with Edge Cloud Zone details.
        """
        pass

    # ArtefactManagement

    @abstractmethod
    def create_artefact_gsma(self, request_body: dict):
        """
        Uploads application artefact on partner OP. Artefact is a zip file
        containing scripts and/or packaging files like Terraform or Helm
        which are required to create an instance of an application

        :param request_body: Payload with artefact information.
        :return:
        """
        pass

    @abstractmethod
    def get_artefact_gsma(self, artefact_id: str) -> Dict:
        """
        Retrieves details about an artefact

        :param artefact_id: Unique identifier of the artefact.
        :return: Dictionary with artefact details.
        """
        pass

    @abstractmethod
    def delete_artefact_gsma(self, artefact_id: str):
        """
        Removes an artefact from partners OP.

        :param artefact_id: Unique identifier of the artefact.
        :return:
        """
        pass

    # ApplicationOnboardingManagement

    @abstractmethod
    def onboard_app_gsma(self, request_body: dict):
        """
        Submits an application details to a partner OP.
        Based on the details provided, partner OP shall do bookkeeping,
        resource validation and other pre-deployment operations.

        :param request_body: Payload with onboarding info.
        :return:
        """
        pass

    @abstractmethod
    def get_onboarded_app_gsma(self, app_id: str) -> Dict:
        """
        Retrieves application details from partner OP

        :param app_id: Identifier of the application onboarded.
        :return: Dictionary with application details.
        """
        pass

    @abstractmethod
    def patch_onboarded_app_gsma(self, app_id: str, request_body: dict):
        """
        Updates partner OP about changes in application compute resource requirements,
        QOS Profile, associated descriptor or change in associated components

        :param app_id: Identifier of the application onboarded.
        :param request_body: Payload with updated onboarding info.
        :return:
        """
        pass

    @abstractmethod
    def delete_onboarded_app_gsma(self, app_id: str):
        """
        Deboards an application from specific partner OP zones

        :param app_id: Identifier of the application onboarded.
        :return:
        """
        pass

    # ApplicationDeploymentManagement

    @abstractmethod
    def deploy_app_gsma(self, request_body: dict) -> Dict:
        """
        Instantiates an application on a partner OP zone.

        :param request_body: Payload with deployment info.
        :return: Dictionary with deployment details.
        """
        pass

    @abstractmethod
    def get_deployed_app_gsma(self, app_id: str, app_instance_id: str, zone_id: str) -> Dict:
        """
        Retrieves an application instance details from partner OP.

        :param app_id: Identifier of the app.
        :param app_instance_id: Identifier of the deployed instance.
        :param zone_id: Identifier of the zone
        :return: Dictionary with application instance details
        """
        pass

    @abstractmethod
    def get_all_deployed_apps_gsma(self, app_id: str, app_provider: str) -> List:
        """
        Retrieves all instances for a given application of partner OP

        :param app_id: Identifier of the app.
        :param app_provider: App provider
        :return: List with application instances details
        """
        pass

    @abstractmethod
    def undeploy_app_gsma(self, app_id: str, app_instance_id: str, zone_id: str):
        """
        Terminate an application instance on a partner OP zone.

        :param app_id: Identifier of the app.
        :param app_instance_id: Identifier of the deployed app.
        :param zone_id: Identifier of the zone
        :return:
        """
        pass
