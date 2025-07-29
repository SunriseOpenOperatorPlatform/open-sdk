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

from requests import Response


class EdgeCloudManagementInterface(ABC):
    """
    Abstract Base Class for Edge Application Management.
    """

    # ====================================================================
    # CAMARA EDGE CLOUD MANAGEMENT API
    # ====================================================================

    # --------------------------------------------------------------------
    # Edge Cloud Zone Management (CAMARA)
    # --------------------------------------------------------------------

    @abstractmethod
    def get_edge_cloud_zones(
        self, region: Optional[str] = None, status: Optional[str] = None
    ) -> Response:
        """
        Retrieves a list of available Edge Cloud Zones.

        :param region: Filter by geographical region.
        :param status: Filter by status (active, inactive, unknown).
        :return: List of Edge Cloud Zones.
        """
        # TODO: Evaluate if the CAMARA-input format
        # TODO: Evaluate the CAMARA-return format
        pass

    # --------------------------------------------------------------------
    # Application Management (CAMARA)
    # --------------------------------------------------------------------

    @abstractmethod
    def onboard_app(self, app_manifest: Dict) -> Response:
        """
        Onboards an app, submitting application metadata
        to the Edge Cloud Provider.

        :param app_manifest: Application metadata in dictionary format.
        :return: Dictionary containing created application details.
        """
        pass

    @abstractmethod
    def get_all_onboarded_apps(self) -> Response:
        """
        Retrieves a list of onboarded applications.

        :return: Response with list of application metadata.
        """
        pass

    @abstractmethod
    def get_onboarded_app(self, app_id: str) -> Response:
        """
        Retrieves information of a specific onboarded application.

        :param app_id: Unique identifier of the application.
        :return: Response with application details.
        """
        pass

    @abstractmethod
    def delete_onboarded_app(self, app_id: str) -> Response:
        """
        Deletes an application onboarded from the Edge Cloud Provider.

        :param app_id: Unique identifier of the application.
        :return: Response confirming deletion.
        """
        pass

    @abstractmethod
    def deploy_app(self, app_id: str, app_zones: List[Dict]) -> Response:
        """
        Requests the instantiation of an application instance.

        :param app_id: Unique identifier of the application.
        :param app_zones: List of Edge Cloud Zones where the app should be
        instantiated.
        :return: Response with instance details.
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
    def undeploy_app(self, app_instance_id: str) -> Response:
        """
        Terminates a specific application instance.

        :param app_instance_id: Unique identifier of the application instance.
        :return: Response confirming termination.
        """
        pass

    # ====================================================================
    # GSMA EDGE COMPUTING API (EWBI OPG) - FEDERATION
    # ====================================================================

    # --------------------------------------------------------------------
    # Federation Management (GSMA)
    # --------------------------------------------------------------------

    @abstractmethod
    def get_edge_cloud_zones_list_gsma(self) -> List:
        """
        Retrieves details of all Zones

        :return: List.
        """
        pass

    @abstractmethod
    def get_edge_cloud_zones_gsma(self, federation_context_id: str) -> List:
        """
        Retrieves details of Zones

        :param federation_context_id: Identifier of the federation context.
        :return: List.
        """
        pass

    # --------------------------------------------------------------------
    # Availability Zone Info Synchronization (GSMA)
    # --------------------------------------------------------------------

    @abstractmethod
    def availability_zone_info_gsma(
        self, federation_context_id: str, request_body: dict
    ) -> Dict:
        """
        Originating OP informs partner OP that it is willing to access
        the specified zones and partner OP shall reserve compute and
        network resources for these zones.

        :param federation_context_id: Identifier of the federation context.
        :param request_body: Payload.
        :return:
        """
        pass

    @abstractmethod
    def get_edge_cloud_zone_details_gsma(
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

    # --------------------------------------------------------------------
    # Artefact Management (GSMA)
    # --------------------------------------------------------------------

    @abstractmethod
    def create_artefact_gsma(
        self, federation_context_id: str, request_body: dict
    ) -> Dict:
        """
        Create Artefact.

        :param federation_context_id: Identifier of the federation context.
        :param request_body: Payload containing artefact details.
        :return: Dictionary with created artefact details.
        """
        pass

    @abstractmethod
    def get_artefact_gsma(self, federation_context_id: str, artefact_id: str) -> Dict:
        """
        Get Artefact.

        :param federation_context_id: Identifier of the federation context.
        :param artefact_id: Unique identifier of the artefact.
        :return: Dictionary with artefact details.
        """
        pass

    @abstractmethod
    def delete_artefact_gsma(
        self, federation_context_id: str, artefact_id: str
    ) -> Dict:
        """
        Delete Artefact.

        :param federation_context_id: Identifier of the federation context.
        :param artefact_id: Unique identifier of the artefact.
        :return: Dictionary with deletion confirmation.
        """
        pass

    # --------------------------------------------------------------------
    # Application Management (GSMA)
    # --------------------------------------------------------------------

    @abstractmethod
    def onboard_app_gsma(self, federation_context_id: str, request_body: dict) -> Dict:
        """
        Create onboarded Application.

        :param federation_context_id: Identifier of the federation context.
        :param request_body: Payload containing application onboarding details.
        :return: Dictionary with onboarded application details.
        """
        pass

    @abstractmethod
    def get_onboarded_app_gsma(self, federation_context_id: str, app_id: str) -> Dict:
        """
        Get onboarded Application.

        :param federation_context_id: Identifier of the federation context.
        :param app_id: Unique identifier of the onboarded application.
        :return: Dictionary with onboarded application details.
        """
        pass

    @abstractmethod
    def patch_onboarded_app_gsma(
        self,
        federation_context_id: str,
        app_id: str,
        request_body: dict,
    ) -> Dict:
        """
        Patch onboarded Application.

        :param federation_context_id: Identifier of the federation context.
        :param app_id: Unique identifier of the onboarded application.
        :param request_body: Payload containing patch details.
        :return: Dictionary with updated application details.
        """
        pass

    @abstractmethod
    def delete_onboarded_app_gsma(
        self, federation_context_id: str, app_id: str
    ) -> Dict:
        """
        Delete onboarded Application.

        :param federation_context_id: Identifier of the federation context.
        :param app_id: Unique identifier of the onboarded application.
        :return: Dictionary with deletion confirmation.
        """
        pass

    @abstractmethod
    def deploy_app_gsma(self, federation_context_id: str, request_body: dict) -> Dict:
        """
        Create deployed Application.

        :param federation_context_id: Identifier of the federation context.
        :param request_body: Payload containing application deployment details.
        :return: Dictionary with deployed application details.
        """
        pass

    @abstractmethod
    def get_deployed_app_gsma(
        self,
        federation_context_id: str,
        app_id: str,
        app_instance_id: str,
        zone_id: str,
    ) -> Dict:
        """
        Retrieves an application instance details from partner OP.

        :param federation_context_id: Identifier of the federation context.
        :param app_id: Unique identifier of the application.
        :param app_instance_id: Unique identifier of the application instance.
        :param zone_id: Unique identifier of the Edge Cloud Zone.
        :return: Dictionary with deployed application details.
        """
        pass

    @abstractmethod
    def get_all_deployed_apps_gsma(
        self,
        federation_context_id: str,
        app_id: str,
        app_provider_id: str,
    ) -> Dict:
        """
        Retrieves all application instances of partner OP.

        :param federation_context_id: Identifier of the federation context.
        :param app_id: Unique identifier of the application.
        :param app_provider_id: Unique identifier of the application provider.
        :return: Dictionary with all deployed applications.
        """
        pass

    @abstractmethod
    def undeploy_app_gsma(
        self,
        federation_context_id: str,
        app_id: str,
        app_instance_id: str,
        zone_id: str,
    ) -> Dict:
        """
        Terminate an application instance on a partner OP zone.

        :param federation_context_id: Identifier of the federation context.
        :param app_id: Unique identifier of the application.
        :param app_instance_id: Unique identifier of the application instance.
        :param zone_id: Unique identifier of the Edge Cloud Zone.
        :return: Dictionary with undeployment confirmation.
        """
        pass
