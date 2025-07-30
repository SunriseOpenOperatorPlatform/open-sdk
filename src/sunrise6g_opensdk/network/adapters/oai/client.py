# -*- coding: utf-8 -*-
##
#
# This file is part of the Open SDK
#
# Contributors:
#   - Giulio Carota (giulio.carota@eurecom.fr)
##
from sunrise6g_opensdk import logger
from sunrise6g_opensdk.network.core.base_network_client import BaseNetworkClient
from sunrise6g_opensdk.network.core.schemas import (
    AsSessionWithQoSSubscription,
    CreateSession,
    CreateTrafficInfluence,
    FlowInfo,
    Snssai,
    TrafficInfluSub,
)

log = logger.get_logger(__name__)
supportedQos = ["qos-e", "qos-s", "qos-m", "qos-l"]


class NetworkManager(BaseNetworkClient):
    """
    This client implements the BaseNetworkClient and translates the
    CAMARA APIs into specific HTTP requests understandable by the OAI NEF API.
    """

    capabilities = {"qod", "traffic_influence"}

    def __init__(self, base_url: str, scs_as_id: str = None):
        try:
            super().__init__()
            self.base_url = base_url
            self.scs_as_id = scs_as_id
            log.info(
                f"Initialized OaiNefClient with base_url: {self.base_url} and scs_as_id: {self.scs_as_id}"
            )

        except Exception as e:
            log.error(f"Failed to initialize OaiNefClient: {e}")
            raise e

    def core_specific_qod_validation(self, session_info: CreateSession):
        """
        Validates core-specific parameters for the session creation.

        args:
            session_info: The session information to validate.

        raises:
            ValidationError: If the session information does not meet core-specific requirements.
        """
        if session_info.qosProfile.root not in supportedQos:
            raise OaiValidationError(
                f"QoS profile {session_info.qosProfile} not supported by OAI, supported profiles are {supportedQos}"
            )

        if session_info.device is None or session_info.device.ipv4Address is None:
            raise OaiValidationError("OAI requires UE IPv4 Address to activate QoS")

        if session_info.applicationServer.ipv4Address is None:
            raise OaiValidationError("OAI requires App IPv4 Address to activate QoS")
        return

    def add_core_specific_qod_parameters(
        self,
        session_info: CreateSession,
        subscription: AsSessionWithQoSSubscription,
    ) -> None:
        device_ip = _retrieve_ue_ipv4(session_info)
        server_ip = _retrieve_app_ipv4(session_info)

        # build flow descriptor in oai format using device ip and server ip
        flow_descriptor = f"permit out ip from {device_ip}/32 to {server_ip}/32"
        _add_qod_flow_descriptor(subscription, flow_descriptor)
        _add_qod_snssai(subscription, 1, "FFFFFF")
        subscription.dnn = "oai"

    def add_core_specific_ti_parameters(
        self,
        traffic_influence_info: CreateTrafficInfluence,
        subscription: TrafficInfluSub,
    ):
        # todo oai add dnn, ssnai, afServiceId
        subscription.dnn = "oai"
        subscription.add_snssai(1, "FFFFFF")
        subscription.afServiceId = self.scs_as_id

    def core_specific_traffic_influence_validation(
        self, traffic_influence_info: CreateTrafficInfluence
    ) -> None:
        """
        Validates core-specific parameters for the session creation.

        args:
            session_info: The session information to validate.

        raises:
            ValidationError: If the session information does not meet core-specific requirements.
        """
        # Placeholder for core-specific validation logic
        # This method should be overridden by subclasses if needed

        if (
            traffic_influence_info.device is None
            or traffic_influence_info.device.ipv4Address is None
        ):
            raise OaiValidationError("OAI requires UE IPv4 Address to activate Traffic Influence")


def _retrieve_ue_ipv4(session_info: CreateSession):
    return session_info.device.ipv4Address.root.privateAddress


def _retrieve_app_ipv4(session_info: CreateSession):
    return session_info.applicationServer.ipv4Address


def _add_qod_flow_descriptor(qos_sub: AsSessionWithQoSSubscription, flow_desriptor: str):
    qos_sub.flowInfo = list()
    qos_sub.flowInfo.append(
        FlowInfo(flowId=len(qos_sub.flowInfo) + 1, flowDescriptions=[flow_desriptor])
    )


def _add_qod_snssai(qos_sub: AsSessionWithQoSSubscription, sst: int, sd: str = None):
    qos_sub.snssai = Snssai(sst=sst, sd=sd)


class OaiValidationError(Exception):
    pass
