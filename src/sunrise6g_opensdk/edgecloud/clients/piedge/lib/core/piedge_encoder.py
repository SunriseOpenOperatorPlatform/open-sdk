import json
import logging
import os
import sys
import traceback

# import connexion
import six

from sunrise6g_opensdk.edgecloud.clients.piedge.lib.models.deploy_service_function import (  # noqa: E501
    DeployServiceFunction,
)
from sunrise6g_opensdk.edgecloud.clients.piedge.lib.utils import auxiliary_functions
from sunrise6g_opensdk.edgecloud.clients.piedge.lib.utils.connector_db import (
    ConnectorDB,
)
from sunrise6g_opensdk.edgecloud.clients.piedge.lib.utils.kubernetes_connector import (
    KubernetesConnector,
)

driver = None


def deploy_chain(chain_input):
    for app_ in chain_input["chain_paas_services_order"]:
        for app_details in chain_input["apps"]:
            if app_ == app_details["paas_input_name"]:

                app_details["paas_input_name"] = (
                    chain_input["chain_service_name"] + "-" + app_
                )
                response = deploy_service_function(app_details)

                break
    return "Chain deployed successfully"


def deploy_service_function(
    service_function: DeployServiceFunction,
    connector_db: ConnectorDB,
    kubernetes_connector: KubernetesConnector,
    paas_name=None,
):  # noqa: E501

    # descriptor_paas_input["scaling_type"]="minimize_cost"
    # print(descriptor_paas_input)
    # we need to create the descriptor_paas_ needed for deployment
    # search if app exists in the catalogue

    ser_function_ = connector_db.get_documents_from_collection(
        "service_functions",
        input_type="name",
        input_value=service_function.service_function_name,
    )
    if not ser_function_:
        return "The given service function does not exist in the catalogue"

    # search if node exists in the node catalogue
    # if service_function.location is not None:
    #     node_ = connector_db.get_documents_from_collection("points_of_presence", input_type="location",
    #                                                        input_value=service_function.location)
    #     if not node_:
    #         return "The given location does not exist in the node catalogue"

    final_deploy_descriptor = {}
    # final_deploy_descriptor["name"]=app_[0]["name"]

    # deployed_name= app_[0]["name"]  + "emp"+ descriptor_paas_input["paas_input_name"]
    if paas_name is not None:
        final_deploy_descriptor["paas_name"] = paas_name

    deployed_name = service_function.service_function_instance_name

    deployed_name = auxiliary_functions.prepare_name(deployed_name, driver)

    final_deploy_descriptor["name"] = deployed_name

    final_deploy_descriptor["count-min"] = (
        1 if service_function.count_min is None else service_function.count_min
    )
    final_deploy_descriptor["count-max"] = (
        1 if service_function.count_max is None else service_function.count_max
    )

    if final_deploy_descriptor["count-min"] > final_deploy_descriptor["count-max"]:
        final_deploy_descriptor["count-min"] = final_deploy_descriptor["count-max"]

    if service_function.location is not None:
        final_deploy_descriptor["location"] = service_function.location

    containers = []
    con_ = {}
    con_["image"] = ser_function_[0]["image"]

    if "privileged" in ser_function_[0]:

        con_["privileged"] = ser_function_[0]["privileged"]

    # con_["imagePullPolicy"] = "Always"
    # ports

    application_ports = ser_function_[0].get("application_ports")
    con_["application_ports"] = application_ports

    if service_function.all_node_ports is not None:

        if (
            service_function.all_node_ports == False
            and service_function.node_ports is None
        ):
            return "Please provide the application ports in the field exposed_ports or all_node_ports==true"

        if service_function.all_node_ports:
            con_["exposed_ports"] = application_ports
        else:

            exposed_ports = auxiliary_functions.return_equal_ignore_order(
                application_ports, service_function.node_ports
            )
            if exposed_ports:
                con_["exposed_ports"] = exposed_ports
        # application_ports = ser_function_[0]["application_ports"]
        # con_["application_ports"] = application_ports
        # containers.append(con_)
    else:
        if service_function.node_ports is not None:
            exposed_ports = auxiliary_functions.return_equal_ignore_order(
                application_ports, service_function.node_ports
            )
            if exposed_ports:

                con_["exposed_ports"] = exposed_ports
    containers.append(con_)

    final_deploy_descriptor["containers"] = containers
    # final_deploy_descriptor["restartPolicy"] = "Always"

    # check volumes!!
    req_volumes = []
    if "required_volumes" in ser_function_[0]:
        if ser_function_[0].get("required_volumes") is not None:
            for required_volumes in ser_function_[0]["required_volumes"]:
                req_volumes.append(required_volumes["name"])
    vol_mount = []
    volume_input = []

    if service_function.volume_mounts is not None:
        for volume_mounts in service_function.volume_mounts:

            vo_in = {}

            vo_in["name"] = volume_mounts.name
            vo_in["storage"] = volume_mounts.storage
            volume_input.append(vo_in)
            vol_mount.append(volume_mounts.name)
    if len(vol_mount) != len(req_volumes):
        return (
            "The selected service function requires "
            + str(len(req_volumes))
            + " volume/ volumes "
        )
    else:
        if ser_function_[0].get("required_volumes") is not None:

            result = auxiliary_functions.equal_ignore_order(req_volumes, vol_mount)

            if result is False:
                return (
                    "The selected service function requires "
                    + str(len(req_volumes))
                    + " volume/ volumes. Please check volume names"
                )
            else:
                volumes = []
                for vol in ser_function_[0]["required_volumes"]:
                    for vol_re in service_function.volume_mounts:
                        vol_ = {}
                        if vol["name"] == vol_re.name:
                            vol_["name"] = vol_re.name
                            vol_["storage"] = vol_re.storage
                            vol_["path"] = vol["path"]
                            if "hostpath" in vol:
                                vol_["hostpath"] = vol["hostpath"]
                            volumes.append(vol_)
                final_deploy_descriptor["volumes"] = volumes

    # check env parameters:
    req_env_parameters = []

    if "required_env_parameters" in ser_function_[0]:
        if ser_function_[0].get("required_env_parameters") is not None:
            for required_env_parameters in ser_function_[0]["required_env_parameters"]:
                req_env_parameters.append(required_env_parameters["name"])
    env_names = []
    env_input = []
    if service_function.env_parameters is not None:
        for env_parameters in service_function.env_parameters:
            env_in = {}

            env_in["name"] = env_parameters.name
            if env_parameters.value is not None:
                env_in["value"] = env_parameters.value
            elif env_parameters.value_ref is not None:
                env_in["value_ref"] = env_parameters.value_ref
            env_input.append(env_in)
            env_names.append(env_parameters.name)
    if len(env_names) != len(req_env_parameters):
        return (
            "The selected service function requires "
            + str(len(req_env_parameters))
            + " env parameters"
        )
    else:
        if ser_function_[0].get("required_env_parameters") is not None:

            result = auxiliary_functions.equal_ignore_order(
                req_env_parameters, env_names
            )

            if result is False:
                return (
                    "The selected service function requires "
                    + str(len(req_env_parameters))
                    + " env parameters. Please check names of env parameters"
                )
            else:
                # EnvParameters to dict
                paremeters = []
                for reqenv in ser_function_[0]["required_env_parameters"]:
                    for env_in in service_function.env_parameters:
                        reqenv_ = {}
                        if reqenv["name"] == env_in.name:
                            reqenv_["name"] = env_in.name
                            if env_in.value is not None:
                                reqenv_["value"] = env_in.value
                            elif env_in.value_ref is not None:
                                reqenv_["value_ref"] = env_in.value_ref
                            paremeters.append(reqenv_)
                final_deploy_descriptor["env_parameters"] = paremeters

    ##################START##################### TODO!!!!!!!!!!!!!!!!!!!!1

    # #Get deployed apps to check if app exist (if yes use patch methods)
    # deployed_apps = kubernetes_connector.get_deployed_apps()
    #
    #
    # exists_flag = False
    # for deployed_app in deployed_apps:
    #     if "appname" in deployed_app:
    #         if final_deploy_descriptor["name"] == deployed_app["appname"]:
    #             exists_flag = True
    #             break

    exists_flag = False
    ##################END#####################

    if exists_flag:
        response = kubernetes_connector.patch_service_function(final_deploy_descriptor)
    else:

        response = kubernetes_connector.deploy_service_function(final_deploy_descriptor)
        # insert it to mongo db
        deployed_service_function_db = {}
        deployed_service_function_db["service_function_name"] = ser_function_[0]["name"]
        if service_function.location is not None:
            deployed_service_function_db["location"] = service_function.location
        deployed_service_function_db["instance_name"] = deployed_name

        if service_function.autoscaling_policy is not None:
            deployed_service_function_db["autoscaling_policy"] = (
                service_function.autoscaling_policy
            )

        if "volumes" in final_deploy_descriptor:
            deployed_service_function_db["volumes"] = final_deploy_descriptor["volumes"]
        if "env_parameters" in final_deploy_descriptor:
            deployed_service_function_db["env_parameters"] = final_deploy_descriptor[
                "env_parameters"
            ]

        if "Conflict" not in response:

            if "location" not in deployed_service_function_db:
                deployed_service_function_db["location"] = (
                    "Node is selected by the K8s scheduler"
                )
            connector_db.insert_document_deployed_service_function(
                document=deployed_service_function_db
            )

    return response
    # return "PaaS deployed successfully"
    # except Exception as ce_:

    #     logging.error(traceback.format_exc())
    #     # logging.error("ERROR NAME: ", fname)
    #     # logging.error("ERROR INFO: ", exc_tb.tb_lineno)
    #     return ("An exception occurred :", ce_)


# def initiliaze_edge_nodes():
#     try:

#         nodes = kubernetes_connector.get_PoPs()
#         kubernetes_connector.create_immediate_storageclass()
#         # write it to mongodb
#         nodes_mon=[]

#         nodes_num=0
#         for node in nodes:
#             nodes_num=nodes_num+1
#             node_ = {}
#             node_["name"] = node.name
#             node_["location"] = node.location
#             node_["_id"] = node.id
#             node_["serial"] = node.serial
#             node_["node_type"] = node.node_type
#             #create monitoring url
#             # http://146.124.106.230:3000/d/piedge-k8smaster/k8smaster-node?orgId=1&refresh=1m
#             #node_["stats_url"]="http://146.124.106.230:3000/d/piedge-k8smaster/k8smaster-node?orgId=1&refresh=1m"

#             mon_url=nodes_monitoring.create_monitoring_infra_per_node(node_,nodes_num)
#             # print('MON_URL: '+mon_url)
#             node_["nodeUsageMonitoringURL"]=mon_url
#             # print(node_)
#             connector_db.insert_document_nodes(node_)
#             nodes_mon.append(node_)

#         # #Creating storageclass for each node - Will be mostly used for migrating stateful applications.
#         # for node in nodes:
#         #     kubernetes_connector.create_node_storageclass(node)

#         # #creates storage class with immediate volume binding mode - will be used for pvc migration
#         # for node in nodes:
#         #     kubernetes_connector.create_immediate_storageclass(node)


#         nodes_monitoring.create_monitoring_for_all_infra(nodes_mon)
#         return "Nodes initialized"
#     except Exception as ce_:
#         logging.error(traceback.format_exc())
#         raise Exception("An exception occurred :", ce_)
