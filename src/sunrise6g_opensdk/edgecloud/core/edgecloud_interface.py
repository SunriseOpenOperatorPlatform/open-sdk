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
        # TODO: Evaluate if we can check here the input (it should be CAMARA-compliant)
        # TODO: Evaluate if we can check here the response (it should be CAMARA-compliant)
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
        Requests the instantiation of an application instance

        :param app_id: Unique identifier of the application
        :param app_zones: List of Edge Cloud Zones where the app should be
        instantiated.
        :return: Response with instance details
        """
        pass

    @abstractmethod
    def get_deployed_app(self, app_instance_id: str) -> Response:
        """
        Retrieves information of a specific application instance

        :param app_instance_id: Unique identifier of the application instance
        :return: Response with application instance details
        """
        pass

    @abstractmethod
    def get_all_deployed_apps(
        self,
        app_id: Optional[str] = None,
        app_instance_id: Optional[str] = None,
        region: Optional[str] = None,
    ) -> Response:
        """
        Retrieves information of application instances

        :param app_id: Filter by application ID
        :param app_instance_id: Filter by instance ID
        :param region: Filter by Edge Cloud region
        :return: Response with application instance details
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
    def get_edge_cloud_zones_list_gsma(self) -> Response:
        """
        Retrieves list of all Zones

        :return: Response with Edge Cloud Zones
        """
        pass

    @abstractmethod
    def get_edge_cloud_zones_gsma(self) -> Response:
        """
        Retrieves details of all Zones with compute resources and flavours for GSMA federation.

        :return: Response with zones and detailed resource information.
        """
        pass

    @abstractmethod
    def get_edge_cloud_zone_details_gsma(self, zone_id: str) -> Response:
        """
        Retrieves details of a specific Edge Cloud Zone reserved
        for the specified zone by the partner OP using GSMA federation.

        :param zone_id: Unique identifier of the Edge Cloud Zone.
        :return: Response with Edge Cloud Zone details.
        """
        pass

    # --------------------------------------------------------------------
    # Artefact Management (GSMA)
    # --------------------------------------------------------------------

    @abstractmethod
    def create_artefact_gsma(self, request_body: dict) -> Response:
        """
        Uploads application artefact on partner OP using GSMA federation.
        Artefact is a zip file containing scripts and/or packaging files
        like Terraform or Helm which are required to create an instance of an application.

        :param request_body: Payload with artefact information.
        :return: Response with artefact upload confirmation.
        """
        pass

    @abstractmethod
    def get_artefact_gsma(self, artefact_id: str) -> Response:
        """
        Retrieves details about an artefact from partner OP using GSMA federation.

        :param artefact_id: Unique identifier of the artefact.
        :return: Response with artefact details.
        """
        pass

    @abstractmethod
    def delete_artefact_gsma(self, artefact_id: str) -> Response:
        """
        Removes an artefact from partners OP using GSMA federation.

        :param artefact_id: Unique identifier of the artefact.
        :return: Response with artefact deletion confirmation.
        """
        pass

    # --------------------------------------------------------------------
    # Application Management (GSMA)
    # --------------------------------------------------------------------

    @abstractmethod
    def onboard_app_gsma(self, request_body: dict) -> Response:
        """
        Submits an application details to a partner OP using GSMA federation.
        Based on the details provided, partner OP shall do bookkeeping,
        resource validation and other pre-deployment operations.

        :param request_body: Payload with onboarding info.
        :return: Response with onboarding confirmation.
        """
        pass

    @abstractmethod
    def get_onboarded_app_gsma(self, app_id: str) -> Response:
        """
        Retrieves application details from partner OP using GSMA federation.

        :param app_id: Identifier of the application onboarded.
        :return: Response with application details.
        """
        pass

    @abstractmethod
    def patch_onboarded_app_gsma(self, app_id: str, request_body: dict) -> Response:
        """
        Updates partner OP about changes in application compute resource requirements,
        QOS Profile, associated descriptor or change in associated components using GSMA federation.

        :param app_id: Identifier of the application onboarded.
        :param request_body: Payload with updated onboarding info.
        :return: Response with update confirmation.
        """
        pass

    @abstractmethod
    def delete_onboarded_app_gsma(self, app_id: str) -> Response:
        """
        Deboards an application from specific partner OP zones using GSMA federation.

        :param app_id: Identifier of the application onboarded.
        :return: Response with deboarding confirmation.
        """
        pass

    @abstractmethod
    def deploy_app_gsma(self, request_body: dict) -> Response:
        """
        Create deployed Application.

        :param request_body: Payload with deployment info.
        :return: Response with deployment details.
        """
        pass

    @abstractmethod
    def get_deployed_app_gsma(self, app_id: str, app_instance_id: str, zone_id: str) -> Response:
        """
        Retrieves an application instance details from partner OP.

        :param app_id: Identifier of the app.
        :param app_instance_id: Identifier of the deployed instance.
        :param zone_id: Identifier of the zone
        :return: Response with application instance details
        """
        pass

    @abstractmethod
    def get_all_deployed_apps_gsma(self) -> Response:
        """
        Retrieves all instances for a given application of partner OP

        :param app_id: Identifier of the app.
        :param app_provider: App provider
        :return: Response with application instances details
        """
        pass

    @abstractmethod
    def undeploy_app_gsma(self, app_id: str, app_instance_id: str, zone_id: str) -> Response:
        """
        Terminate an application instance on a partner OP zone.

        :param app_id: Identifier of the app.
        :param app_instance_id: Identifier of the deployed app.
        :param zone_id: Identifier of the zone
        :return: Response with undeployment confirmation
        """
        pass
