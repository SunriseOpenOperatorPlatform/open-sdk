# -*- coding: utf-8 -*-
from pydantic import ValidationError

from sunrise6g_opensdk import logger
from sunrise6g_opensdk.network.core.network_interface import (
    NetworkManagementInterface,
    build_flows,
)

from ...core import schemas

log = logger.get_logger(__name__)

flow_id_mapping = {"qos-e": 3, "qos-s": 4, "qos-m": 5, "qos-l": 6}


class NetworkManager(NetworkManagementInterface):
    """
    This client implements the NetworkManagementInterface and translates the
    CAMARA APIs into specific HTTP requests understandable by the Open5GS NEF API.

    Invloved partners and their roles in this implementation:
    - I2CAT: Responsible for the CAMARA QoD API and its mapping to the
             3GPP AsSessionWithQoS API exposed by Open5GS NEF.
    - NCSRD: Responsible for the CAMARA Location API and its mapping to the
             3GPP Monitoring Event API exposed Open5GS NEF.
    """

    def __init__(self, base_url: str, scs_as_id):
        """
        Initializes the Open5GS Client.
        """
        try:
            self.base_url = base_url
            self.scs_as_id = scs_as_id
            log.info(
                f"Initialized Open5GSClient with base_url: {self.base_url} "
                f"and scs_as_id: {self.scs_as_id}"
            )
        except Exception as e:
            log.error(f"Failed to initialize Open5GSClient: {e}")
            raise e

    def core_specific_qod_validation(self, session_info: schemas.CreateSession):
        if session_info.qosProfile.root not in flow_id_mapping.keys():
            raise ValidationError(
                f"Open5Gs only supports these qos-profiles: {', '.join(flow_id_mapping.keys())}"
            )

    def add_core_specific_qod_parameters(
        self,
        session_info: schemas.CreateSession,
        subscription: schemas.AsSessionWithQoSSubscription,
    ) -> None:
        subscription.supportedFeatures = schemas.SupportedFeatures("003C")
        flow_id = flow_id_mapping[session_info.qosProfile.root]
        subscription.flowInfo = build_flows(flow_id, session_info)


# Note:
# As this class is inheriting from NetworkManagementInterface, it is
# expected to implement all the abstract methods defined in that interface.
#
# In case this network adapter doesn't support a specific method, it should
# be marked as NotImplementedError.
