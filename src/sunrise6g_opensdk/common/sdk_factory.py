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
from sunrise6g_opensdk.edgecloud.clients.aeros.client import (
    EdgeApplicationManager as AerosClient,
)
from sunrise6g_opensdk.edgecloud.clients.i2edge.client import (
    EdgeApplicationManager as I2EdgeClient,
)
from sunrise6g_opensdk.edgecloud.clients.piedge.client import (
    EdgeApplicationManager as PiEdgeClient,
)
from sunrise6g_opensdk.network.clients.oai.client import NetworkManager as OaiCoreClient
from sunrise6g_opensdk.network.clients.open5gcore.client import (
    NetworkManager as Open5GCoreClient,
)
from sunrise6g_opensdk.network.clients.open5gs.client import (
    NetworkManager as Open5GSClient,
)

#


def _edgecloud_factory(client_name: str, base_url: str, **kwargs):
    edge_cloud_factory = {
        "aeros": lambda url, **kw: AerosClient(base_url=url, **kw),
        "i2edge": lambda url: I2EdgeClient(base_url=url),
        "piedge": lambda url: PiEdgeClient(base_url=url),
    }
    try:
        return edge_cloud_factory[client_name](base_url, **kwargs)
    except KeyError:
        raise ValueError(
            f"Invalid edgecloud client '{client_name}'. Available: {list(edge_cloud_factory)}"
        )


def _network_factory(client_name: str, base_url: str, **kwargs):
    if "scs_as_id" not in kwargs:
        raise ValueError("Missing required 'scs_as_id' for network clients.")
    scs_as_id = kwargs.pop("scs_as_id")

    network_factory = {
        "open5gs": lambda url, scs_id, **kw: Open5GSClient(
            base_url=url, scs_as_id=scs_id, **kw
        ),
        "oai": lambda url, scs_id, **kw: OaiCoreClient(
            base_url=url, scs_as_id=scs_id, **kw
        ),
        "open5gcore": lambda url, scs_id, **kw: Open5GCoreClient(
            base_url=url, scs_as_id=scs_id, **kw
        ),
    }
    try:
        return network_factory[client_name](base_url, scs_as_id, **kwargs)
    except KeyError:
        raise ValueError(
            f"Invalid network client '{client_name}'. Available: {list(network_factory)}"
        )


# def _oran_factory(client_name: str, base_url: str):
#     # TODO


class SdkFactory:
    _domain_factories = {
        "edgecloud": _edgecloud_factory,
        "network": _network_factory,
        # "oran": _oran_factory,
    }

    @classmethod
    def instantiate_and_retrieve_clients(
        cls, domain: str, client_name: str, base_url: str, **kwargs
    ):
        try:
            catalog = cls._domain_factories[domain]
        except KeyError:
            raise ValueError(
                f"Unsupported domain '{domain}'. Supported: {list(cls._domain_factories)}"
            )
        return catalog(client_name, base_url, **kwargs)
