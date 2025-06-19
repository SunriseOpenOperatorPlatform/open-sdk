# -*- coding: utf-8 -*-
from pydantic import ValidationError

from sunrise6g_opensdk import logger
from sunrise6g_opensdk.network.core.network_interface import (
    NetworkManagementInterface,
    build_flows,
)

from ...core import schemas

log = logger.get_logger("Open5GCore")  # Usage of brand name

qos_support_map = {
    "qos-e": 1,  # ToDo
    "qos-s": 5,
    "qos-m": 9,
    "qos-l": 9,  # ToDo not yet available in Nokia RAN
}


class NetworkManager(NetworkManagementInterface):
    def __init__(self, base_url: str, scs_as_id: str):
        if not base_url:
            raise ValueError("base_url is required and cannot be empty.")
        if not scs_as_id:
            raise ValueError("scs_as_id is required and cannot be empty.")

        self.base_url = base_url
        self.scs_as_id = scs_as_id

    def core_specific_qod_validation(self, session_info: schemas.CreateSession):
        qos_key = session_info.qosProfile.root.strip().lower()

        if qos_key not in qos_support_map:
            supported = ", ".join(qos_support_map.keys())
            raise ValidationError(
                f"Unsupported QoS profile '{session_info.qosProfile.root}'. "
                f"Supported profiles for Open5GCore are: {supported}"
            )

    def add_core_specific_qod_parameters(
        self,
        session_info: schemas.CreateSession,
        subscription: schemas.AsSessionWithQoSSubscription,
    ) -> None:
        flow_id = qos_support_map[session_info.qosProfile.root]
        subscription.flowInfo = build_flows(flow_id, session_info)
        subscription.ueIpv4Addr = "192.168.6.1"  # ToDo
