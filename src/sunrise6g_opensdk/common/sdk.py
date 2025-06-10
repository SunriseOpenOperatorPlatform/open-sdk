# -*- coding: utf-8 -*-
##
# Copyright 2025-present by Software Networks Area, i2CAT.
# All rights reserved.
#
# This file is part of the Open SDK
#
# Contributors:
#   - Adrián Pino Martínez (adrian.pino@i2cat.net)
##
from typing import Dict

from sunrise6g_opensdk.common.sdk_factory import SdkFactory


class Sdk:
    @staticmethod
    def create_clients_from(
        client_specs: Dict[str, Dict[str, str]],
    ) -> Dict[str, object]:
        """
        Create and return a dictionary of instantiated edgecloud/network/oran clients
        based on the provided specifications.

        Args:
            client_specs (dict): A dictionary where each key is the client's domain (e.g., 'edgecloud', 'network'),
                                 and each value is a dictionary containing:
                                 - 'client_name' (str): The specific name of the client (e.g., 'i2edge', 'open5gs').
                                 - 'base_url' (str): The base URL for the client's API.
                                 Additional parameters like 'scs_as_id' may also be included.

        Returns:
            dict: A dictionary where keys are the 'client_name' (str) and values are
                  the instantiated client objects.

        Example:
            >>> from src.common.universal_client_catalog import UniversalCatalogClient
            >>>
            >>> client_specs_example = {
            >>>     'edgecloud': {
            >>>         'client_name': 'i2edge',
            >>>         'base_url': 'http://ip_edge_cloud:port',
            >>>         'additionalEdgeCloudParamater1': 'example'
            >>>     },
            >>>     'network': {
            >>>         'client_name': 'open5gs',
            >>>         'base_url': 'http://ip_network:port',
            >>>         'additionalNetworkParamater1': 'example'
            >>>     }
            >>> }
            >>>
            >>> clients = UniversalCatalogClient.create_clients(client_specs_example)
            >>> edgecloud_client = clients.get("edgecloud")
            >>> network_client = clients.get("network")
            >>>
            >>> edgecloud_client.get_edge_cloud_zones()
            >>> network_client.get_qod_session(session_id="example_session_id")
        """
        sdk_client = SdkFactory()
        clients = {}

        for domain, config in client_specs.items():
            client_name = config["client_name"]
            base_url = config["base_url"]

            # Support of additional paramaters for specific clients
            kwargs = {
                k: v for k, v in config.items() if k not in ("client_name", "base_url")
            }

            client = sdk_client.instantiate_and_retrieve_clients(
                domain, client_name, base_url, **kwargs
            )
            clients[domain] = client

        return clients
