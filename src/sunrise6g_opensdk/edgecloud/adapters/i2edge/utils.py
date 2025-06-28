#!/usr/bin/env python3
# -*- coding: utf-8 -*-
##
# This file is part of the Open SDK
#
# Contributors:
#   - Sergio Giménez (sergio.gimenez@i2cat.net)
#   - César Cajas (cesar.cajas@i2cat.net)
##
import uuid
from typing import Optional, Union
from uuid import UUID

from src.edgecloud import logger

from sunrise6g_opensdk.edgecloud.api.routers.lcm.schemas import RequiredResources
from sunrise6g_opensdk.edgecloud.core import utils as core_utils

from .client import I2EdgeClient
from .common import I2EdgeError

log = logger.get_logger(__name__)


def generate_namespace_name_from(app_id: str, app_instance_id: str) -> str:
    max_length = 63
    combined_name = "{}-{}".format(app_id, app_instance_id)
    if len(combined_name) > max_length:
        combined_name = combined_name[:max_length]
    return combined_name


def generate_unique_id() -> UUID:
    return uuid.uuid4()


def instantiate_app_with(
    camara_app_id: UUID,
    zone_id: str,
    required_resources: RequiredResources,
    i2edge: I2EdgeClient,
) -> tuple[str, str]:
    memory_size_str = "{}GB".format(required_resources.memory + 1)
    num_gpus = core_utils.get_num_gpus_from(required_resources)
    try:
        flavour_id = i2edge.create_flavour(
            zone_id=zone_id,
            memory_size=memory_size_str,
            num_cpu=required_resources.numCPU,
            num_gpus=num_gpus,
        )
        i2edge_instance_id = generate_unique_id()
        application_k8s_namespace = generate_namespace_name_from(
            str(camara_app_id), str(i2edge_instance_id)
        )
        i2edge.deploy_app(
            appId=str(camara_app_id),
            zoneId=zone_id,
            flavourId=flavour_id,
            namespace=application_k8s_namespace,
        )
        return flavour_id, application_k8s_namespace
    except I2EdgeError as e:
        err_msg = "Error instantiating app {} in zone {}".format(camara_app_id, zone_id)
        log.error("{}. Detailed error: {}".format(err_msg, e))
        raise e


def onboard_app_with(
    application_id: UUID,
    artefact_id: UUID,
    app_name: str,
    app_version: Optional[str],  # TODO pass this to i2edge
    repo_type: str,
    app_repo: str,
    user_name: Optional[str],
    password: Optional[str],
    token: Optional[str],
    i2edge: I2EdgeClient,
):
    try:
        # TODO Come back to handle errors when onboarding and perform rollbacks
        i2edge.create_artefact(
            artefact_id=str(artefact_id),
            artefact_name=app_name,
            repo_name=app_name,
            repo_type=repo_type,
            repo_url=app_repo,
            user_name=user_name,
            password=password,
            token=token,
        )

        i2edge.onboard_app(app_id=str(application_id), artefact_id=str(application_id))
    except I2EdgeError as e:
        err_msg = "Error onboarding app {} in i2edge".format(app_name)
        log.error("{}. Detailed error: {}".format(err_msg, e))
        raise e


def delete_app_instance_by(
    namespace: str, flavour_id: str, zone_id: str, i2edge: I2EdgeClient
):
    i2edge_app_instance_name = get_app_name_from(namespace, i2edge)
    if i2edge_app_instance_name is None:
        err_msg = "Couldn't retrieve app instance from I2Edge."
        log.error(err_msg)
        raise I2EdgeError(err_msg)
    i2edge.undeploy_app(i2edge_app_instance_name)
    i2edge.delete_flavour(flavour_id=str(flavour_id), zone_id=zone_id)


def get_app_name_from(namespace: str, i2edge: I2EdgeClient) -> Union[str, None]:
    try:
        response = i2edge.get_all_deployed_apps()
        for deployment in response:
            if deployment.get("bodytosend", {}).get("namespace") == namespace:
                return deployment.get("name")
        return None
    except I2EdgeError as e:
        err_msg = "Error getting app name for namespace {}".format(namespace)
        log.error("{}. Detailed error: {}".format(err_msg, e))
        raise e


def delete_app_by(app_id: UUID, artefact_id: UUID, i2edge: I2EdgeClient):
    try:
        i2edge.delete_onboarded_app(app_id=str(app_id))
        i2edge.delete_artefact(artefact_id=str(artefact_id))
    except I2EdgeError as e:
        err_msg = "Error deleting app {}".format(app_id)
        log.error("{}. Detailed error: {}".format(err_msg, e))
        raise e


def get_edgecloud_zones(i2edge: I2EdgeClient) -> list[str]:
    try:
        zone_ids = []
        response = i2edge.get_zones_list()
        for zone in response:
            zone_id = zone.get("zoneId")
            if zone_id is not None:
                zone_ids.append(zone_id)
        return zone_ids

    except I2EdgeError as e:
        err_msg = "Error getting zones from i2edge"
        log.error("{}. Detailed error: {}".format(err_msg, e))
        raise e
