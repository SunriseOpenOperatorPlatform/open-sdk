from __future__ import print_function

from urllib.parse import urlparse

import requests
import urllib3
from kubernetes import client
from kubernetes.client.rest import ApiException

from sunrise6g_opensdk.edgecloud.adapters.kubernetes.lib.utils import (
    auxiliary_functions,
)
from sunrise6g_opensdk.edgecloud.adapters.kubernetes.lib.utils.connector_db import (
    ConnectorDB,
)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

configuration = client.Configuration()


class KubernetesConnector:
    def __init__(self, ip, port, token, username, namespace):
        parsed_url = urlparse(ip)  # ip can be full URL or just IP

        scheme = parsed_url.scheme or "https"
        host = parsed_url.hostname or ip
        port = port or parsed_url.port or "6443"

        self.host = f"{scheme}://{host}:{port}"
        self.namespace = namespace if namespace else "default"
        self.token_k8s = token

        configuration.api_key["authorization"] = self.token_k8s
        configuration.api_key_prefix["authorization"] = "Bearer"

        configuration.host = self.host

        configuration.username = username
        configuration.verify_ssl = False
        self.v1 = client.CoreV1Api(client.ApiClient(configuration))

        # config.lod
        # client.Configuration.set_default(configuration)
        # Defining host is optional and default to http://localhost
        # Enter a context with an instance of the API kubernetes.client
        with client.ApiClient(configuration) as api_client:
            # Create an instance of the API class
            self.api_instance = client.AdmissionregistrationApi(api_client)
            self.api_instance_appsv1 = client.AppsV1Api(api_client)
            self.api_instance_apiregv1 = client.ApiregistrationV1Api(api_client)
            self.api_instance_v1autoscale = client.AutoscalingV1Api(api_client)
            # self.api_instance_v2beta1autoscale = client.AutoscalingV2beta1Api(
            #     api_client
            # )
            # self.api_instance_v2beta2autoscale = client.AutoscalingV2beta1Api(
            #     api_client
            # )
            self.api_instance_corev1api = client.CoreV1Api(api_client)
            self.api_instance_storagev1api = client.StorageV1Api(api_client)
            self.api_instance_batchv1 = client.BatchV1Api(api_client)

            self.api_custom = client.CustomObjectsApi(api_client)
            try:
                self.api_instance.get_api_group()
            except ApiException as e:
                print("Exception when calling AdmissionregistrationApi->get_api_group: %s\n" % e)

    def get_node_details(self):
        try:
            url = self.host + "/api/v1/nodes"
            headers = {"Authorization": "Bearer " + self.token_k8s}
            x = requests.get(url, headers=headers, verify=False)
            node_details = x.json()
            return node_details
        except requests.exceptions.HTTPError as e:
            # logging.error(traceback.format_exc())
            return "Exception when calling Kubernetes API:" + e.args

    def get_PoP_statistics(self, nodeName):

        # x1 = v1.list_node().to_dict()

        try:
            url = self.host + "/api/v1/nodes"
            headers = {"Authorization": "Bearer " + self.token_k8s}
            x = requests.get(url, headers=headers, verify=False)
            x1 = x.json()
        except requests.exceptions.HTTPError as e:
            # logging.error(traceback.format_exc())
            return (
                "Exception when calling CoreV1Api->/api/v1/namespaces/sunrise6g/persistentvolumeclaims: %s\n"
                % e
            )
        k8s_nodes = self.api_custom.list_cluster_custom_object("metrics.k8s.io", "v1beta1", "nodes")

        # client.models.v1_node_list.V1NodeList
        # kubernetes.client.models.v1_node_list.V1NodeList\

        pop_output = {}
        for pop in x1["items"]:

            name = pop["metadata"]["name"]
            if name == nodeName:
                pop_output["nodeName"] = name
                pop_output["nodeId"] = pop["metadata"]["uid"]
                pop_output["nodeLocation"] = pop["metadata"]["labels"]["location"]

                node_addresses = {}
                node_addresses["nodeHostName"] = pop["status"]["addresses"][1]["address"]
                node_addresses["nodeExternalIP"] = pop["status"]["addresses"][0]["address"]
                node_addresses["nodeInternalIP"] = pop["metadata"]["annotations"].get(
                    "projectcalico.org/IPv4VXLANTunnelAddr"
                )
                pop_output["nodeAddresses"] = node_addresses

                node_conditions = {}
                for condition in pop["status"]["conditions"]:
                    type = condition["type"]
                    node_type = "node" + type
                    node_conditions[node_type] = condition["status"]
                pop_output["nodeConditions"] = node_conditions

                node_capacity = {}
                node_capacity["nodeCPUCap"] = pop["status"]["capacity"]["cpu"]
                memory = pop["status"]["capacity"]["memory"]
                memory_size = len(memory)
                node_capacity["nodeMemoryCap"] = memory[: memory_size - 2]
                node_capacity["nodeMemoryCapMU"] = memory[-2:]
                storage = pop["status"]["capacity"]["ephemeral-storage"]
                storage_size = len(storage)
                node_capacity["nodeStorageCap"] = storage[: storage_size - 2]
                node_capacity["nodeStorageCapMU"] = storage[-2:]
                node_capacity["nodeMaxNoofPods"] = pop["status"]["capacity"]["pods"]
                pop_output["nodeCapacity"] = node_capacity

                node_allocatable_resources = {}
                node_allocatable_resources["nodeCPUCap"] = pop["status"]["allocatable"]["cpu"]
                memory = pop["status"]["allocatable"]["memory"]
                memory_size = len(memory)
                node_allocatable_resources["nodeMemoryCap"] = memory[: memory_size - 2]
                node_allocatable_resources["nodeMemoryCapMU"] = memory[-2:]
                storage = pop["status"]["allocatable"]["ephemeral-storage"]
                storage_size = len(storage)
                node_allocatable_resources["nodeStorageCap"] = storage[: storage_size - 2]
                node_allocatable_resources["nodeStorageCapMU"] = storage[-2:]
                # node_allocatable_resources["nodeMaxNoofPods"] = pop['status']['allocatable']['pods']
                pop_output["nodeAllocatableResources"] = node_allocatable_resources

                # calculate usage
                for stats in k8s_nodes["items"]:
                    if stats["metadata"]["name"] == nodeName:
                        node_usage = {}
                        cpu = stats["usage"]["cpu"]
                        cpu_size = len(cpu)
                        memory = stats["usage"]["memory"]
                        memory_size = len(memory)

                        node_usage["nodeMemoryInUse"] = memory[: memory_size - 2]
                        node_usage["nodeMemoryInUseMU"] = memory[-2:]
                        node_usage["nodeMemoryUsage"] = int(node_usage["nodeMemoryInUse"]) / int(
                            node_capacity["nodeMemoryCap"]
                        )
                        node_usage["nodeCPUInUse"] = cpu[: cpu_size - 1]
                        node_usage["nodeCPUInUseMU"] = cpu[-1:]
                        node_usage["nodeCPUUsage"] = int(node_usage["nodeCPUInUse"]) / (
                            int(node_capacity["nodeCPUCap"]) * 1000
                        )
                        pop_output["nodeUsage"] = node_usage

                node_general_info = {}
                node_general_info["nodeOS"] = pop["status"]["nodeInfo"]["osImage"]
                node_general_info["nodeKubernetesVersion"] = pop["status"]["nodeInfo"][
                    "kernelVersion"
                ]
                node_general_info["nodecontainerRuntimeVersion"] = pop["status"]["nodeInfo"][
                    "containerRuntimeVersion"
                ]
                node_general_info["nodeKernelVersion"] = pop["status"]["nodeInfo"]["kernelVersion"]
                node_general_info["nodeArchitecture"] = pop["status"]["nodeInfo"]["architecture"]
                pop_output["nodeGeneralInfo"] = node_general_info

        return pop_output

    def get_PoPs(self):

        try:
            pops_ = []
            x1 = self.v1.list_node()
            for node in x1.items:
                pop_ = {}
                pop_["name"] = node.metadata.name
                pop_["uid"] = node.metadata.uid
                pop_["location"] = node.metadata.labels.get("location")
                pop_["serial"] = node.status.addresses[0].address
                pop_["node_type"] = node.metadata.labels.get("node_type")
                pop_["status"] = (
                    "active" if node.status.conditions[-1].status == "True" else "inactive"
                )
                # pop_= NodesResponse(id=uid,name=name,location=location,serial=address, node_type=node_type, status=ready_status)
                pops_.append(pop_)
            return pops_
        # url = host + "/api/v1/nodes"
        # headers = {"Authorization": "Bearer " + token_k8s}
        # x=requests.get(url, headers=headers, verify=False)
        # x1 = x.json()
        except requests.exceptions.HTTPError as e:
            # logging.error(traceback.format_exc())
            return (
                "Exception when calling CoreV1Api->/api/v1/namespaces/sunrise6g/persistentvolumeclaims: %s\n"
                % e
            )

    #

    def delete_service_function(self, connector_db: ConnectorDB, service_function_name):
        self.api_instance_appsv1.delete_namespaced_deployment(
            name=service_function_name, namespace=self.namespace
        )

        self.v1.delete_namespaced_service(name=service_function_name, namespace=self.namespace)

        hpa_list = self.api_instance_v1autoscale.list_namespaced_horizontal_pod_autoscaler(
            self.namespace
        )

        # hpas=hpa_list["items"]

        for hpa in hpa_list.items:
            if hpa.metadata.name == service_function_name:
                self.api_instance_v1autoscale.delete_namespaced_horizontal_pod_autoscaler(
                    name=service_function_name, namespace=self.namespace
                )
                break
        # deletevolume
        volume_list = self.v1.list_namespaced_persistent_volume_claim(self.namespace)
        for volume in volume_list.items:
            name_v = service_function_name + str("-")
            if name_v in volume.metadata.name:
                self.v1.delete_persistent_volume(name=volume.spec.volume_name)

                self.v1.delete_namespaced_persistent_volume_claim(
                    name=volume.metadata.name, namespace=self.namespace
                )

        doc = {}
        doc["instance_name"] = service_function_name
        connector_db.delete_document_deployed_service_functions(document=doc)

    def deploy_service_function(self, descriptor_service_function):
        # deploys a Deployment yaml file, a service, a pvc and a hpa

        if "volumes" in descriptor_service_function:
            for volume in descriptor_service_function["volumes"]:
                # first solution (python k8s client arises error without reason!)
                # body_volume = create_pvc(descriptor_service_function["name"], volume)
                # api_response_pvc = v1.create_namespaced_persistent_volume_claim("sunrise6g", body_volume)

                # #deploy pv
                # print("deploy pv")
                # try:
                #     url = host + "/api/v1/persistentvolumes"
                #     body_volume = create_pv_dict(descriptor_service_function["name"], volume)
                #
                #
                #     headers = {"Authorization": "Bearer " + token_k8s}
                #     x = requests.post(url, headers=headers, json=body_volume, verify=False)
                #     print (x.status_code)
                # except requests.exceptions.HTTPError as e:
                #     # logging.error(traceback.format_exc())
                #     return ("Exception when calling CoreV1Api->/api/v1/persistentvolumes: %s\n" % e)

                # deploy pvc

                if volume.get("hostpath") is None:
                    try:
                        url = (
                            self.host
                            + "/api/v1/namespaces/"
                            + self.namespace
                            + "/persistentvolumeclaims"
                        )
                        body_volume = self.create_pvc_dict(
                            descriptor_service_function["name"], volume
                        )
                        headers = {"Authorization": "Bearer " + self.token_k8s}
                        requests.post(url, headers=headers, json=body_volume, verify=False)
                    except requests.exceptions.HTTPError as e:
                        # logging.error(traceback.format_exc())
                        return (
                            "Exception when calling CoreV1Api->/api/v1/namespaces/"
                            + self.namespace
                            + "/persistentvolumeclaims: %s\n" % e
                        )

                # api_response_pvc = api_instance_corev1api.create_namespaced_persistent_volume_claim
        body_deployment = self.create_deployment(descriptor_service_function)
        body_service = self.create_service(descriptor_service_function)

        try:
            api_response_deployment = self.api_instance_appsv1.create_namespaced_deployment(
                self.namespace, body_deployment
            )
            # api_response_service = api_instance_apiregv1.create_api_service(body_service)
            self.v1.create_namespaced_service(self.namespace, body_service)
            if "autoscaling_policies" in descriptor_service_function:
                # V1 AUTOSCALER
                body_hpa = self.create_hpa(descriptor_service_function)
                self.api_instance_v1autoscale.create_namespaced_horizontal_pod_autoscaler(
                    self.namespace, body_hpa
                )
                # V2beta1 AUTOSCALER
                # body_hpa = create_hpa(descriptor_paas)
                # api_instance_v2beta1autoscale.create_namespaced_horizontal_pod_autoscaler("sunrise6g",body_hpa)

            return api_response_deployment
        except ApiException as e:
            # logging.error(traceback.format_exc())
            return (
                "Exception when calling AppsV1Api->create_namespaced_deployment or ApiregistrationV1Api->create_api_service: %s\n"
                % e
            )
        # Exception("An exception occurred : ", e)

    def create_deployment(self, descriptor_service_function):
        metadata = client.V1ObjectMeta(name=descriptor_service_function["name"])
        dict_label = {self.namespace: descriptor_service_function["name"]}
        selector = client.V1LabelSelector(match_labels=dict_label)
        metadata_spec = client.V1ObjectMeta(labels=dict_label)

        containers = []
        for container in descriptor_service_function["containers"]:
            security_context = self._get_security_context(container)
            ports = self._get_container_ports(container)
            envs = self._get_env_vars(descriptor_service_function)
            volumes, volume_mounts = self._get_volumes_and_mounts(descriptor_service_function)

            if "autoscaling_policies" in descriptor_service_function:
                resources = self._get_resource_requirements(descriptor_service_function)
                con = client.V1Container(
                    name=descriptor_service_function["name"],
                    image=container["image"],
                    ports=ports,
                    image_pull_policy="Always",
                    resources=resources,
                    env=envs if envs else None,
                    volume_mounts=volume_mounts if volume_mounts else None,
                    security_context=security_context,
                )
            else:
                con = client.V1Container(
                    name=descriptor_service_function["name"],
                    image=container["image"],
                    ports=ports,
                    image_pull_policy="Always",
                    env=envs if envs else None,
                    volume_mounts=volume_mounts if volume_mounts else None,
                    security_context=security_context,
                )
            containers.append(con)

        template_spec_ = self._get_pod_spec(descriptor_service_function, containers, volumes)
        template = client.V1PodTemplateSpec(metadata=metadata_spec, spec=template_spec_)

        spec = client.V1DeploymentSpec(
            selector=selector,
            template=template,
            replicas=descriptor_service_function["count-min"],
        )

        body = client.V1Deployment(
            api_version="apps/v1", kind="Deployment", metadata=metadata, spec=spec
        )
        return body

    def _get_security_context(self, container):
        if "privileged" in container:
            return client.V1SecurityContext(privileged=container["privileged"])
        return None

    def _get_container_ports(self, container):
        ports = []
        for port_id in container.get("application_ports", []):
            ports.append(client.V1ContainerPort(container_port=port_id))
        return ports

    def _get_env_vars(self, descriptor_service_function):
        envs = []
        if (
            "env_parameters" in descriptor_service_function
            and descriptor_service_function["env_parameters"] is not None
        ):
            for env in descriptor_service_function["env_parameters"]:
                if "value" in env:
                    envs.append(client.V1EnvVar(name=env["name"], value=env["value"]))
                elif "value_ref" in env and "paas_name" in descriptor_service_function:
                    env_name_ = self._resolve_env_value_ref(
                        env["value_ref"], descriptor_service_function
                    )
                    envs.append(client.V1EnvVar(name=env["name"], value=env_name_))
        return envs

    def _resolve_env_value_ref(self, value_ref, descriptor_service_function):
        env_split = value_ref.split(":")
        if "@" not in value_ref:
            if len(env_split) > 2:
                prefix = env_split[0]
                final_env = env_split[1]
                split2 = final_env.split("//")
                if len(split2) >= 2:
                    final_env = split2[1]
                port_env = env_split[2]
                env_ = auxiliary_functions.prepare_name_for_k8s(
                    str(descriptor_service_function["paas_name"]) + "-" + final_env
                )
                return f"{prefix}://{env_}:{port_env}"
            elif len(env_split) > 1:
                final_env = env_split[0]
                port_env = env_split[1]
                env_ = auxiliary_functions.prepare_name_for_k8s(
                    str(descriptor_service_function["paas_name"]) + "-" + final_env
                )
                return f"{env_}:{port_env}"
            else:
                final_env = env_split[0]
                return auxiliary_functions.prepare_name_for_k8s(
                    str(descriptor_service_function["paas_name"]) + "-" + final_env
                )
        return value_ref

    def _get_volumes_and_mounts(self, descriptor_service_function):
        volumes = []
        volume_mounts = []
        if (
            "volumes" in descriptor_service_function
            and descriptor_service_function["volumes"] is not None
        ):
            for volume in descriptor_service_function["volumes"]:
                vol_name = str(descriptor_service_function["name"]) + "-" + volume["name"]
                if volume.get("hostpath") is None:
                    pvc = client.V1PersistentVolumeClaimVolumeSource(claim_name=vol_name)
                    volume_ = client.V1Volume(name=vol_name, persistent_volume_claim=pvc)
                else:
                    hostpath = client.V1HostPathVolumeSource(path=volume["hostpath"])
                    volume_ = client.V1Volume(name=vol_name, host_path=hostpath)
                volumes.append(volume_)
                volume_mount = client.V1VolumeMount(name=vol_name, mount_path=volume["path"])
                volume_mounts.append(volume_mount)
        return volumes, volume_mounts

    def _get_resource_requirements(self, descriptor_service_function):
        limits_dict = {}
        request_dict = {}
        for auto_scale_policy in descriptor_service_function.get("autoscaling_policies", []):
            limits_dict[auto_scale_policy["metric"]] = auto_scale_policy["limit"]
            request_dict[auto_scale_policy["metric"]] = auto_scale_policy["request"]
        return client.V1ResourceRequirements(limits=limits_dict, requests=request_dict)

    def _get_pod_spec(self, descriptor_service_function, containers, volumes):
        if "location" in descriptor_service_function:
            node_selector_dict = {"nodeName": descriptor_service_function["location"]}
            return client.V1PodSpec(
                containers=containers,
                node_selector=node_selector_dict,
                hostname=descriptor_service_function["name"],
                restart_policy="Always",
                volumes=volumes if volumes else None,
            )
        else:
            return client.V1PodSpec(
                containers=containers,
                hostname=descriptor_service_function["name"],
                restart_policy="Always",
                volumes=volumes if volumes else None,
            )

    def create_service(self, descriptor_service_function):
        dict_label = {}
        dict_label[self.namespace] = descriptor_service_function["name"]
        metadata = client.V1ObjectMeta(name=descriptor_service_function["name"], labels=dict_label)

        #  spec

        if (
            "exposed_ports" in descriptor_service_function["containers"][0]
        ):  # create NodePort svc object
            ports = []
            hepler = 0
            for port_id in descriptor_service_function["containers"][0]["exposed_ports"]:

                # if "grafana" in descriptor_service_function["name"]:
                #     ports_=client.V1ServicePort(port=port_id,
                #                                 node_port=31000,
                #                                 target_port=port_id, name=str(port_id))
                # else:
                #     ports_ = client.V1ServicePort(port=port_id,
                #                                   # node_port=descriptor_paas["containers"][0]["exposed_ports"][hepler],
                #                                   target_port=port_id, name=str(port_id))
                ports_ = client.V1ServicePort(port=port_id, target_port=port_id, name=str(port_id))
                ports.append(ports_)
                hepler = hepler + 1
            spec = client.V1ServiceSpec(selector=dict_label, ports=ports, type="NodePort")
            # body = client.V1Service(api_version="v1", kind="Service", metadata=metadata, spec=spec)
        else:  # create ClusterIP svc object
            ports = []
            for port_id in descriptor_service_function["containers"][0]["application_ports"]:
                ports_ = client.V1ServicePort(port=port_id, target_port=port_id, name=str(port_id))
                ports.append(ports_)
            spec = client.V1ServiceSpec(selector=dict_label, ports=ports, type="ClusterIP")
        body = client.V1Service(api_version="v1", kind="Service", metadata=metadata, spec=spec)

        return body

    def create_pvc(self, name, volumes):
        dict_label = {}
        name_vol = name + str("-") + volumes["name"]
        dict_label[self.namespace] = name_vol
        # metadata = client.V1ObjectMeta(name=name_vol)
        metadata = client.V1ObjectMeta(name=name_vol, labels=dict_label)
        # api_version = ("v1",)
        kind = ("PersistentVolumeClaim",)
        spec = client.V1PersistentVolumeClaimSpec(
            access_modes=["ReadWriteMany"],
            resources=client.V1ResourceRequirements(requests={"storage": volumes["storage"]}),
        )
        body = client.V1PersistentVolumeClaim(
            api_version="v1", kind=kind, metadata=metadata, spec=spec
        )

        return body

    def create_pvc_dict(self, name, volumes, storage_class="microk8s-hostpath", volume_name=None):
        name_vol = name + str("-") + volumes["name"]
        # body={}
        # body["api_version"]="v1"
        # body["kind"]="PersistentVolumeClaim"
        # metadata={}
        # labels={}
        body = {
            "api_version": "v1",
            "kind": "PersistentVolumeClaim",
            "metadata": {"labels": {self.namespace: name_vol}, "name": name_vol},
            "spec": {
                "accessModes": ["ReadWriteOnce"],
                "resources": {"requests": {"storage": volumes["storage"]}},
                "storageClassName": storage_class,
            },
        }

        if volume_name is not None:
            body["spec"]["volume_name"] = volume_name

        return body

    def create_pv_dict(self, name, volumes, storage_class, node=None):
        name_vol = name + "-" + volumes["name"]

        body = {
            "apiVersion": "v1",
            "kind": "PersistentVolume",
            "metadata": {
                "name": name_vol,
                "labels": {
                    self.namespace: name_vol,
                },
            },
            "spec": {
                "capacity": {"storage": volumes["storage"]},
                "volumeMode": "Filesystem",
                "accessModes": ["ReadWriteOnce"],
                "persistentVolumeReclaimPolicy": "Delete",
                "storageClassName": storage_class,
                "hostPath": {"path": "/mnt/" + name_vol, "type": "DirectoryOrCreate"},
            },
        }

        if node is not None:
            body["spec"]["nodeAffinity"] = {
                "required": {
                    "nodeSelectorTerms": [
                        {
                            "matchExpressions": [
                                {
                                    "key": "kubernetes.io/hostname",
                                    "operator": "In",
                                    "values": [node],
                                }
                            ]
                        }
                    ]
                }
            }

        return body

    def check_for_update_hpas(self, deployed_hpas):

        for hpa in deployed_hpas:
            for catalogue_policy in hpa["catalogue_policy"]:
                if catalogue_policy["policy"] == hpa["deployed_scaling_type"]:
                    for metrics in catalogue_policy["monitoring_metrics"]:

                        if metrics["metric_name"] == hpa["deployed_metric"]:

                            if (
                                metrics["catalogue_util"] != hpa["deployed_util"]
                            ):  # need to update hpa
                                desc_paas = {}
                                desc_paas["name"] = hpa["name"]
                                desc_paas["count-max"] = hpa["max"]
                                desc_paas["count-min"] = hpa["min"]
                                policy = {}
                                policy["limit"] = metrics["catalogue_limit"]
                                policy["request"] = metrics["catalogue_request"]
                                policy["util_percent"] = metrics["catalogue_util"]
                                policy["metric_name"] = metrics["metric_name"]
                                policies = []
                                policies.append(policy)
                                desc_paas["autoscaling_policies"] = policies
                                body_hpa = self.create_hpa(desc_paas)
                                self.api_instance_v1autoscale.patch_namespaced_horizontal_pod_autoscaler(
                                    namespace=self.namespace,
                                    name=desc_paas["name"],
                                    body=body_hpa,
                                )
                            break
                    break

    def create_hpa(descriptor_service_function):

        # V1!!!!!!!

        dict_label = {}
        dict_label["name"] = descriptor_service_function["name"]
        metadata = client.V1ObjectMeta(name=descriptor_service_function["name"], labels=dict_label)

        #  spec

        scale_target = client.V1CrossVersionObjectReference(
            api_version="apps/v1",
            kind="Deployment",
            name=descriptor_service_function["name"],
        )

        # todo!!!! check 0 gt an exoume kai cpu k ram auto dn tha einai auto to version!
        spec = client.V1HorizontalPodAutoscalerSpec(
            max_replicas=descriptor_service_function["count-max"],
            min_replicas=descriptor_service_function["count-min"],
            target_cpu_utilization_percentage=int(
                descriptor_service_function["autoscaling_policies"][0]["util_percent"]
            ),
            scale_target_ref=scale_target,
        )
        body = client.V1HorizontalPodAutoscaler(
            api_version="autoscaling/v1",
            kind="HorizontalPodAutoscaler",
            metadata=metadata,
            spec=spec,
        )

        return body

    def get_deployed_dataspace_connector(self, instance_name):
        api_response = self.api_instance_appsv1.list_namespaced_deployment(self.namespace)

        api_response_service = self.v1.list_namespaced_service(self.namespace)
        app_ = {}
        for app in api_response.items:
            metadata = app.metadata
            app.spec
            status = app.status

            dataspace_name = instance_name + "-dataspace-connector"

            if dataspace_name == metadata.name:

                app_["dataspace_connector_name"] = metadata.name

            if app_:  # if app_ is not empty

                if (status.available_replicas is not None) and (status.ready_replicas is not None):
                    if status.available_replicas >= 1 and status.ready_replicas >= 1:
                        app_["status"] = "running"
                        app_["replicas"] = status.ready_replicas
                    else:
                        app_["status"] = "not_running"
                        app_["replicas"] = 0
                else:
                    app_["status"] = "not_running"
                    app_["replicas"] = 0

                for app_service in api_response_service.items:

                    metadata_svc = app_service.metadata

                    spec_svc = app_service.spec
                    svc_ports = []
                    if metadata_svc.name == app_["dataspace_connector_name"]:
                        app_["internal_ip"] = spec_svc.cluster_ip
                        for port in spec_svc.ports:
                            port_ = {}
                            if port.node_port is not None:

                                port_["exposed_port"] = port.node_port
                                port_["protocol"] = port.protocol
                                port_["application_port"] = port.port
                                svc_ports.append(port_)
                            else:
                                port_["protocol"] = port.protocol
                                port_["application_port"] = port.port
                                svc_ports.append(port_)
                        app_["ports"] = svc_ports
                        break
                return app_
        return app_

    def get_deployed_service_functions(self, connector_db: ConnectorDB):
        self.get_deployed_hpas(connector_db)
        api_response = self.api_instance_appsv1.list_namespaced_deployment(self.namespace)
        api_response_service = self.v1.list_namespaced_service(self.namespace)
        api_response_pvc = self.v1.list_namespaced_persistent_volume_claim(self.namespace)

        apps_col = connector_db.get_documents_from_collection(collection_input="service_functions")
        deployed_apps_col = connector_db.get_documents_from_collection(
            collection_input="deployed_service_functions"
        )
        nodes = connector_db.get_documents_from_collection(collection_input="points_of_presence")

        apps = []
        for app in api_response.items:
            app_ = self._build_app_dict(app, apps_col, deployed_apps_col, api_response_pvc, nodes)
            if app_:
                self._add_service_ports(app_, api_response_service)
                apps.append(app_)
        return apps

    def _build_app_dict(self, app, apps_col, deployed_apps_col, api_response_pvc, nodes):
        metadata = app.metadata
        spec = app.spec
        status = app.status
        app_ = {}
        actual_name = None
        for app_col in deployed_apps_col:
            if metadata.name == app_col["instance_name"]:
                app_["service_function_instance_name"] = app_col["instance_name"]
                actual_name = app_col["name"]
                app_["appInstanceId"] = app_col["_id"]
                if "monitoring_service_URL" in app_col:
                    app_["monitoring_service_URL"] = app_col["monitoring_service_URL"]
                if "paas_name" in app_col:
                    app_["paas_name"] = app_col["paas_name"]
                break
        for app_col in apps_col:
            if actual_name == app_col["name"]:
                app_["service_function_catalogue_name"] = app_col["name"]
                app_["appId"] = app_col["_id"]
                app_["appProvider"] = app_col.get("app_provider")
                break

        # find volumes!
        for app_col in apps_col:
            if app_col.get("required_volumes") is not None:
                volumes_ = []
                for volume in app_col["required_volumes"]:
                    for item in api_response_pvc.items:
                        name_v = str("-") + volume["name"]
                        if name_v in item.metadata.name and metadata.name in item.metadata.name:
                            volumes_.append(item.metadata.name)
                            app_["volumes"] = volumes_
                            break
                break

        if not app_:
            return None

        # Set status and replicas
        if (status.available_replicas is not None) and (status.ready_replicas is not None):
            if status.available_replicas >= 1 and status.ready_replicas >= 1:
                app_["status"] = "ready"
                app_["replicas"] = status.ready_replicas
            else:
                app_["status"] = "failed"
                app_["replicas"] = 0
        else:
            app_["status"] = "failed"
            app_["replicas"] = 0

        # Find compute node
        if (
            spec.template.spec.node_selector is not None
            and "location" in spec.template.spec.node_selector.keys()
        ):
            location = spec.template.spec.node_selector["location"]
            for node in nodes:
                if location == node["location"]:
                    app_["node_name"] = node["name"]
                    app_["node_id"] = node["_id"]
                    app_["location"] = node["location"]
                    break

        return app_

    def _add_service_ports(self, app_, api_response_service):
        for app_service in api_response_service.items:
            metadata_svc = app_service.metadata
            spec_svc = app_service.spec
            svc_ports = []
            if metadata_svc.name == app_["service_function_instance_name"]:
                for port in spec_svc.ports:
                    port_ = {}
                    if port.node_port is not None:
                        port_["exposed_port"] = port.node_port
                        port_["protocol"] = port.protocol
                        port_["application_port"] = port.port
                        svc_ports.append(port_)
                    else:
                        port_["protocol"] = port.protocol
                        port_["application_port"] = port.port
                        svc_ports.append(port_)
                app_["ports"] = svc_ports
                break

    def get_deployed_hpas(self, connector_db: ConnectorDB):
        # APPV1 Implementation!
        api_response = self.api_instance_v1autoscale.list_namespaced_horizontal_pod_autoscaler(
            self.namespace
        )

        hpas = []
        for hpa in api_response.items:
            metadata = hpa.metadata
            spec = hpa.spec
            hpa_ = {}

            deployed_hpas_col = connector_db.get_documents_from_collection(
                collection_input="deployed_apps"
            )
            apps_col = connector_db.get_documents_from_collection(collection_input="paas_services")

            actual_name = None
            for hpa_col in deployed_hpas_col:
                if metadata.name == hpa_col["deployed_name"]:
                    hpa_["name"] = metadata.name
                    if "scaling_type" in hpa_col:
                        hpa_["deployed_scaling_type"] = hpa_col["scaling_type"]

                    actual_name = hpa_col["name"]
                    break
            for app_col in apps_col:
                if actual_name == app_col["name"]:
                    hpa_["paascataloguename"] = app_col["name"]
                    hpa_["appid"] = app_col["_id"]
                    if "autoscaling_policies" in app_col:
                        pol = []
                        for autoscaling_ in app_col["autoscaling_policies"]:

                            metric_ = []
                            for auto_metric in autoscaling_["monitoring_metrics"]:
                                hpa__ = {}
                                # if auto_metric["metric_name"]=="cpu": #TODO!! CHANGE IT FOR v1beta2 etc.....!!!!! (only cpu wokrs now)
                                hpa__["catalogue_util"] = auto_metric["util_percent"]
                                hpa__["metric_name"] = auto_metric["metric_name"]
                                hpa__["catalogue_limit"] = auto_metric["limit"]
                                hpa__["catalogue_request"] = auto_metric["request"]
                                metric_.append(hpa__)
                                # pol["monitoring_metrics"]=  metric_

                            polic = {}
                            polic["policy"] = autoscaling_["policy"]
                            polic["monitoring_metrics"] = metric_
                            pol.append(polic)

                        hpa_["catalogue_policy"] = pol
                    break

            if hpa_:  # if hpa_ is empty
                hpa_["min"] = spec.min_replicas
                hpa_["max"] = spec.max_replicas
                hpa_["deployed_util"] = spec.target_cpu_utilization_percentage
                hpa_["deployed_metric"] = "cpu"

                hpas.append(hpa_)

        return hpas

    def is_job_completed(self, job_name):
        job = self.api_instance_batchv1.read_namespaced_job(name=job_name, namespace=self.namespace)
        if job.status.succeeded is not None and job.status.succeeded > 0:
            return True
        return False

    # Create storageClass resource for a node - useless for now
    def create_immediate_storageclass(self, node=None):
        api_version = "storage.k8s.io/v1"
        kind = "StorageClass"
        name = "immediate-storageclass"
        provisioner = "microk8s.io/hostpath"
        reclaim_policy = "Delete"
        volume_binding_mode = "Immediate"

        metadata = client.V1ObjectMeta(name=name)

        # match_label_expressions = client.V1TopologySelectorLabelRequirement(key='kubernetes.io/hostname', values=[node.name])
        #
        # topology_selector_term = client.V1TopologySelectorTerm([match_label_expressions])

        # storage_class = client.V1StorageClass(api_version=api_version, kind=kind, metadata=metadata, provisioner=provisioner
        #                                       , volume_binding_mode=volume_binding_mode, reclaim_policy=reclaim_policy
        #                                       , allowed_topologies=[topology_selector_term])

        storage_class = client.V1StorageClass(
            api_version=api_version,
            kind=kind,
            metadata=metadata,
            provisioner=provisioner,
            volume_binding_mode=volume_binding_mode,
            reclaim_policy=reclaim_policy,
        )

        try:
            self.api_instance_storagev1api.create_storage_class(body=storage_class)
        except ApiException as e:
            print("Exception when calling StorageV1Api->create_storage_class: %s\n" % e)

    def immediate_storage_class_exists(self):
        try:
            storage_classes = self.api_instance_storagev1api.list_storage_class().items()

            for sc in storage_classes:
                if sc.metadata.name == "immediate-storageclass":
                    return True

            return False

        except ApiException as e:
            return f"Exception when calling StorageV1Api->list_storage_class: {e}"
