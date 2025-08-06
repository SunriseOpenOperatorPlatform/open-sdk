from kubernetes.client import V1Deployment

from sunrise6g_opensdk.edgecloud.adapters.kubernetes.lib.models.deploy_service_function import (  # noqa: E501
    DeployServiceFunction,
)
from sunrise6g_opensdk.edgecloud.adapters.kubernetes.lib.utils import (
    auxiliary_functions,
)
from sunrise6g_opensdk.edgecloud.adapters.kubernetes.lib.utils.connector_db import (
    ConnectorDB,
)
from sunrise6g_opensdk.edgecloud.adapters.kubernetes.lib.utils.kubernetes_connector import (
    KubernetesConnector,
)

driver = None


def prepare_container(service_function, ser_function_):
    containers = []
    con_ = {}
    con_["image"] = ser_function_[0]["image"]
    if "privileged" in ser_function_[0]:
        con_["privileged"] = ser_function_[0]["privileged"]
    application_ports = ser_function_[0]["application_ports"]
    con_["application_ports"] = application_ports

    if service_function.all_node_ports is not None:
        if service_function.all_node_ports is False and service_function.node_ports is None:
            return (
                "Please provide the application ports in the field exposed_ports or all_node_ports==true",
                400,
            )
        if service_function.all_node_ports:
            con_["exposed_ports"] = application_ports
        else:
            exposed_ports = auxiliary_functions.return_equal_ignore_order(
                application_ports, service_function.node_ports
            )
            if exposed_ports:
                con_["exposed_ports"] = exposed_ports
    else:
        if service_function.node_ports is not None:
            exposed_ports = auxiliary_functions.return_equal_ignore_order(
                application_ports, service_function.node_ports
            )
            if exposed_ports:
                con_["exposed_ports"] = exposed_ports
    containers.append(con_)
    return containers


def prepare_volumes(service_function, ser_function_, final_deploy_descriptor):
    req_volumes = []
    if "required_volumes" in ser_function_[0]:
        if ser_function_[0]["required_volumes"] is not None:
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
            "The selected service function requires " + str(len(req_volumes)) + " volume/ volumes ",
            400,
        )
    else:
        if ser_function_[0].get("required_volumes") is not None:
            result = auxiliary_functions.equal_ignore_order(req_volumes, vol_mount)
            if result is False:
                return (
                    "The selected service function requires "
                    + str(len(req_volumes))
                    + " volumes. Please check volume names",
                    400,
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
    return None


def prepare_env_parameters(service_function, ser_function_, final_deploy_descriptor):
    req_env_parameters = []
    if "required_env_parameters" in ser_function_[0]:
        if ser_function_[0]["required_env_parameters"] is not None:
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
            + " env parameters",
            400,
        )
    else:
        if ser_function_[0].get("required_env_parameters") is not None:
            result = auxiliary_functions.equal_ignore_order(req_env_parameters, env_names)
            if result is False:
                return (
                    "The selected service function requires "
                    + str(len(req_env_parameters))
                    + " env parameters. Please check names of env parameters",
                    400,
                )
            else:
                paremeters = []
                for reqenv in ser_function_[0].get("required_env_parameters"):
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
    return None


def deploy_service_function(
    service_function: DeployServiceFunction,
    connector_db: ConnectorDB,
    kubernetes_connector: KubernetesConnector,
    paas_name=None,
):

    ser_function_ = connector_db.get_documents_from_collection(
        "service_functions",
        input_type="name",
        input_value=service_function.service_function_name,
    )
    if not ser_function_:
        return "The given service function does not exist in the catalogue", 404

    final_deploy_descriptor = {}
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

    containers = prepare_container(service_function, ser_function_)
    if isinstance(containers, tuple):
        return containers
    final_deploy_descriptor["containers"] = containers

    vol_result = prepare_volumes(service_function, ser_function_, final_deploy_descriptor)
    if vol_result is not None:
        return vol_result

    env_result = prepare_env_parameters(service_function, ser_function_, final_deploy_descriptor)
    if env_result is not None:
        return env_result

    response = kubernetes_connector.deploy_service_function(final_deploy_descriptor)
    deployed_service_function_db = {}
    deployed_service_function_db["service_function_name"] = ser_function_[0]["name"]
    if service_function.location is not None:
        deployed_service_function_db["location"] = service_function.location
    deployed_service_function_db["instance_name"] = deployed_name

    if "volumes" in final_deploy_descriptor:
        deployed_service_function_db["volumes"] = final_deploy_descriptor["volumes"]
    if "env_parameters" in final_deploy_descriptor:
        deployed_service_function_db["env_parameters"] = final_deploy_descriptor["env_parameters"]

    if "location" not in deployed_service_function_db:
        deployed_service_function_db["location"] = "Node is selected by the K8s scheduler"
    if type(response) is V1Deployment:
        deployed_service_function_db["_id"] = response.metadata.uid
        connector_db.insert_document_deployed_service_function(
            document=deployed_service_function_db
        )
    return response
