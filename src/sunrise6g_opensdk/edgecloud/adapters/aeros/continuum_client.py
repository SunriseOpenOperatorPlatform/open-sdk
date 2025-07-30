##
# This file is part of the Open SDK
#
# Contributors:
#   - Vasilis Pitsilis (vpitsilis@dat.demokritos.gr, vpitsilis@iit.demokritos.gr)
#   - Andreas Sakellaropoulos (asakellaropoulos@iit.demokritos.gr)
##
"""
aerOS REST API Client
   This client is used to interact with the aerOS REST API.
"""

import requests

from sunrise6g_opensdk.edgecloud.adapters.aeros import config
from sunrise6g_opensdk.edgecloud.adapters.aeros.utils import catch_requests_exceptions
from sunrise6g_opensdk.logger import setup_logger


class ContinuumClient:
    """
    Client to aerOS ngsi-ld based continuum exposure
    """

    def __init__(self, base_url: str = None):
        """
        :param base_url: the base url of the aerOS API
        """
        if base_url is None:
            self.api_url = config.aerOS_API_URL
        else:
            self.api_url = base_url
        self.logger = setup_logger(__name__, is_debug=True, file_name=config.LOG_FILE)
        self.m2m_cb_token = config.aerOS_ACCESS_TOKEN
        self.hlo_token = config.aerOS_HLO_TOKEN
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "aerOS": "true",
            "Authorization": f"Bearer {self.m2m_cb_token}",
        }
        self.hlo_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "aerOS": "true",
            "Authorization": f"Bearer {self.hlo_token}",
        }
        self.hlo_onboard_headers = {
            "Content-Type": "application/yaml",
            "Authorization": f"Bearer {self.hlo_token}",
        }

    @catch_requests_exceptions
    def query_entity(self, entity_id, ngsild_params) -> dict:
        """
        Query entity with ngsi-ld params
        :input
        @param entity_id: the id of the queried entity
        @param ngsi-ld: the query params
        :output
        ngsi-ld object
        """
        entity_url = f"{self.api_url}/entities/{entity_id}?{ngsild_params}"
        response = requests.get(entity_url, headers=self.headers, timeout=15)
        if response is None:
            return None
        else:
            if config.DEBUG:
                self.logger.debug("Query entity URL: %s", entity_url)
                self.logger.debug(
                    "Query entity response: %s %s", response.status_code, response.text
                )
            return response.json()

    @catch_requests_exceptions
    def query_entities(self, ngsild_params):
        """
        Query entities with ngsi-ld params
        :input
        @param ngsi-ld: the query params
        :output
        ngsi-ld object
        """
        entities_url = f"{self.api_url}/entities?{ngsild_params}"
        response = requests.get(entities_url, headers=self.headers, timeout=15)
        if response is None:
            return None
        # else:
        #     if config.DEBUG:
        #         self.logger.debug("Query entities URL: %s", entities_url)
        #         self.logger.debug("Query entities response: %s %s",
        #                           response.status_code, response.text)
        return response.json()

    @catch_requests_exceptions
    def deploy_service(self, service_id: str) -> dict:
        """
        Re-allocate (deploy) service  on aerOS continuum
        :input
        @param service_id: the id of the service to be re-allocated
        :output
        the re-allocated service json object
        """
        re_allocate_url = f"{self.api_url}/hlo_fe/services/{service_id}"
        response = requests.put(re_allocate_url, headers=self.hlo_headers, timeout=15)
        if response is None:
            return None
        else:
            if config.DEBUG:
                self.logger.debug("Re-allocate service URL: %s", re_allocate_url)
                self.logger.debug(
                    "Re-allocate service response: %s %s",
                    response.status_code,
                    response.text,
                )
            return response.json()

    @catch_requests_exceptions
    def undeploy_service(self, service_id: str) -> dict:
        """
        Undeploy service
        :input
        @param service_id: the id of the service to be undeployed
        :output
        the undeployed service json object
        """
        undeploy_url = f"{self.api_url}/hlo_fe/services/{service_id}"
        response = requests.delete(undeploy_url, headers=self.hlo_headers, timeout=15)
        if response is None:
            return None
        else:
            if config.DEBUG:
                self.logger.debug("Re-allocate service URL: %s", undeploy_url)
                self.logger.debug(
                    "Undeploy service response: %s %s",
                    response.status_code,
                    response.text,
                )
            return response.json()

    @catch_requests_exceptions
    def onboard_and_deploy_service(self, service_id: str, tosca_str: str) -> dict:
        """
        Onboard (& deploy) service  on aerOS continuum
        :input
        @param service_id: the id of the service to onboarded (& deployed)
        @param tosca_str: the tosca whith all orchestration information
        :output
        the allocated service json object
        """
        onboard_url = f"{self.api_url}/hlo_fe/services/{service_id}"
        if config.DEBUG:
            self.logger.debug("Onboard service URL: %s", onboard_url)
            self.logger.debug("Onboard service request body (TOSCA-YAML): %s", tosca_str)
        response = requests.post(
            onboard_url, data=tosca_str, headers=self.hlo_onboard_headers, timeout=15
        )
        if response is None:
            return None
        else:
            if config.DEBUG:
                self.logger.debug("Onboard service URL: %s", onboard_url)
                self.logger.debug(
                    "Onboard service response: %s %s",
                    response.status_code,
                    response.text,
                )
            return response.json()

    @catch_requests_exceptions
    def purge_service(self, service_id: str) -> bool:
        """
        Purge service from aerOS continuum
        :input
        @param service_id: the id of the service to be purged
        :output
        the purge result message from aerOS continuum
        """
        purge_url = f"{self.api_url}/hlo_fe/services/{service_id}/purge"
        response = requests.delete(purge_url, headers=self.hlo_headers, timeout=15)
        if response is None:
            return False
        else:
            if config.DEBUG:
                self.logger.debug("Purge service URL: %s", purge_url)
                self.logger.debug(
                    "Purge service response: %s %s",
                    response.status_code,
                    response.text,
                )
            if response.status_code != 200:
                self.logger.error("Failed to purge service: %s", response.text)
                return False
            return True
