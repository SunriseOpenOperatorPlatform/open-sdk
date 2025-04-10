# Mocked API for testing purposes
from typing import Dict, List, Optional
import os
import logging
import requests
from edgecloud.core.edgecloud_interface import EdgeCloudManagementInterface
from swagger_server.utils import kubernetes_connector, connector_db
from swagger_server.models.service_function_registration_request import ServiceFunctionRegistrationRequest
from swagger_server.models.deploy_service_function import DeployServiceFunction
from swagger_server.core.piedge_encoder import deploy_service_function

piedge_ip = os.environ['EDGE_CLOUD_ADAPTER']
edge_cloud_provider = os.environ['PLATFORM_PROVIDER']

class EdgeApplicationManager(EdgeCloudManagementInterface):
    def onboard_app(self, app_manifest: Dict) -> Dict:
        print(f"Submitting application: {app_manifest}")
        logging.info('Extracting variables from payload...')
        app_name = app_manifest.get('name')
        image = app_manifest.get('appRepo').get('imagePath')
        sf = ServiceFunctionRegistrationRequest(service_function_image=image, service_function_name=app_name)
        return sf

    def get_all_onboarded_apps(self) -> List[Dict]:
        logging.info('Retrieving all registered apps from database...')
        app_list = connector_db.get_documents_from_collection(collection_input="service_functions")
        return app_list
        # return [{"appId": "1234-5678", "name": "TestApp"}]

    def get_onboarded_app(self, app_id: str) -> Dict:
        logging.info('Searching for registered app with ID: '+ app_id+' in database...')
        app = connector_db.get_documents_from_collection("service_functions", input_type="_id", input_value=app_id)
        return app

    def delete_onboarded_app(self, app_id: str) -> None:
        logging.info('Deleting registered app with ID: '+ app_id+' from database...')
        result = connector_db.delete_document_service_function(app_id)
        return result
        # print(f"Deleting application: {app_id}")

    def deploy_app(self, app_id: str, app_zones: List[Dict]) -> Dict:
        logging.info('Searching for registered app with ID: '+ app_id+' in database...')
        app = connector_db.get_documents_from_collection("service_functions", input_type="_id", input_value=app_id)
        success_response = []
        if app is not None:
            for zone in app_zones:
                sf = DeployServiceFunction(service_function_name=app.get('name'), 
                                           service_function_instance_name=app.get('name')+zone.get('edgeCloudZoneName'), 
                                           location=zone.get('edgeCloudZoneName'))
                result = deploy_service_function(service_function=sf)
                success_response.append(result)
        # return {"appInstanceId": "abcd-efgh"}
        return success_response

    def get_all_deployed_apps(self, app_id: Optional[str] = None, app_instance_id: Optional[str] = None, region: Optional[str] = None) -> List[Dict]:
        logging.info('Retreiving all deployed apps in the edge cloud platform')
        response = kubernetes_connector.get_deployed_service_functions()
        return [{"appInstanceId": "abcd-efgh", "status": "ready"}]

    def undeploy_app(self, app_instance_id: str) -> None:
        logging.info('Searching for deployed app with ID: '+ app_instance_id+' in database...')
        print(f"Deleting app instance: {app_instance_id}")
        # deployed_service_function_name_=auxiliary_functions.prepare_name_for_k8s(deployed_service_function_name)
        sfs=kubernetes_connector.get_deployed_service_functions()
        response = 'App instance with ID ['+app_instance_id+'] not found'
        for service_fun in sfs.items:
            if service_fun["uid"]==app_instance_id:
                response = kubernetes_connector.delete_service_function(service_fun['service_function_instance_name'])
        return response        


    def get_edge_cloud_zones(self, region: Optional[str] = None, status: Optional[str] = None) -> List[Dict]:
        
        nodes_response = kubernetes_connector.get_PoPs()
        zone_list =[]
        
        for node in nodes_response.json().get('nodes'):
                zone = {}
                zone['edgeCloudZoneId'] = node.get('uid')
                zone['edgeCloudZoneName'] = node.get('name')
                zone['edgeCloudZoneStatus'] = node.get('status')
                zone['edgeCloudProvider'] = edge_cloud_provider
                zone['edgeCloudRegion'] = node.get('location')
                zone_list.append(zone)
        return zone_list
    
