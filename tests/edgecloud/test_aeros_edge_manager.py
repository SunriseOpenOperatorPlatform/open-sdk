##
# This file is part of the Open SDK
# Temporary file for testing aerOS EdgeApplicationManager class
#
# Contributors:
#   - Vasilis Pitsilis (vpitsilis@dat.demokritos.gr, vpitsilis@iit.demokritos.gr)
#   - Andreas Sakellaropoulos (asakellaropoulos@iit.demokritos.gr)
##
"""
aerOS continuum, SUNRISE-6G SDK  unit testing.
Please do not run in the same pass all of:
  test_onboard_app_success, test_undeploy_app_completes_successfully, test_deploy_app_returns_app_instance_id
Leave uncommented just one of them each time.
Also environment variables must be sset in advance, regarding access tokens
  see also config.py file in aerOS tree
"""
import unittest
from typing import Any, Dict

from sunrise6g_opensdk.edgecloud.clients.aeros.client import EdgeApplicationManager

TOSCA_YAML_EXAMPLE: str = """
tosca_definitions_version: tosca_simple_yaml_1_3

description: TOSCA for network performance

node_templates:
  influxdb:
    type: tosca.nodes.Container.Application
    requirements:
      - network:
          properties:
            ports:
              fastapi:
                properties:
                  protocol: [tcp]
                  source: 8086
            exposePorts: true
      - host:
          node_filter:
            properties:
              id: "urn:ngsi-ld:InfrastructureElement:CloudFerro:fa163e5e25ef"
    artifacts:
      influxdb-image:
        file: p4lik4ri/influxdb
        type: tosca.artifacts.Deployment.Image.Container.Docker
        repository: docker_hub
    interfaces:
      Standard:
        create:
          implementation: influxdb-image
          inputs:
            envVars:
              - ENV1: void


"""


class TestAerOSEdgeApplicationManager(unittest.TestCase):
    """
    Test aerOS EdgeApplicationManager class
    Test aerOS ContinuumClient class
    """

    def setUp(self):
        self.manager = EdgeApplicationManager(
            base_url="https://ncsrd-mvp-domain.aeros-project.eu"
        )

    # def test_get_all_onboarded_apps_returns_list_of_dicts(self):
    #     '''
    #         Test if get_all_onboarded_apps returns a list of dictionaries
    #         Check if the list contains at least one known item.
    #     '''
    #     result = self.manager.get_all_onboarded_apps()

    #     # Check it's a list
    #     self.assertIsInstance(result, list)
    #     self.assertTrue(all(isinstance(entry, dict) for entry in result))

    #     # Check if at least one known item is in the list
    #     expected_entry = {
    #         "appId": "urn:ngsi-ld:Service:xai-service",
    #         "name": "aeros_service_urn:ngsi-ld:Service:xai-service"
    #     }
    #     self.assertIn(expected_entry, result)

    # def test_get_onboarded_app_returns_expected_keys(self):
    #     '''
    #         Test if get_onboarded_app returns a dictionary with expected keys
    #         Check against an existing "onboarded/deployed" service.
    #     '''
    #     # Use an existing app ID known to be "onboarded" in aerOS
    #     app_id = "urn:ngsi-ld:Service:xai-service"

    #     result = self.manager.get_onboarded_app(app_id)

    #     self.assertIsInstance(result, dict)
    #     self.assertIn("appId", result)
    #     self.assertIn("name", result)

    #     # Check specific known values
    #     self.assertEqual(result["appId"], app_id)
    #     self.assertEqual(result["name"],
    #                      "aeros_service_urn:ngsi-ld:Service:xai-service")

    # def test_get_all_deployed_apps_returns_list(self):
    #     '''
    #         Test if get_all_deployed_apps returns a list of dictionaries
    #         Check if list items (dicts) contain CAMARA expected keys.
    #     '''
    #     result = self.manager.get_all_deployed_apps()

    #     self.assertIsInstance(result, list)
    #     self.assertGreater(len(result),
    #                        0)  # Expecting at least one app instance

    #     for item in result:
    #         self.assertIn("appInstanceId", item)
    #         self.assertIn("status", item)

    # def test_get_all_deployed_apps_filter_by_app_id(self):
    #     '''
    #         Test if get_all_deployed_apps returns a list of dictionaries
    #           when providing an app_id.
    #         Check if list items (dicts) contain CAMARA expected keys
    #           and service component name (appId) is one of the two
    #           components of the provided service.
    #     '''
    #     app_id = "urn:ngsi-ld:Service:xai-service"

    #     result = self.manager.get_all_deployed_apps(app_id=app_id)

    #     self.assertIsInstance(result, list)

    #     for item in result:
    #         self.assertIn("appInstanceId", item)
    #         self.assertIn("status", item)
    #         self.assertIsInstance(item["status"], str)
    #         self.assertIn(item["appInstanceId"], [
    #             "urn:ngsi-ld:Service:xai-service:Component:server-side",
    #             "urn:ngsi-ld:Service:xai-service:Component:broker-side"
    #         ])

    # def test_get_edge_cloud_zones_returns_valid_list(self):
    #     '''
    #         Test if get_edge_cloud_zones returns a list of dictionaries
    #         Check if item NCSRD aerOS domain is contained in return object.
    #     '''
    #     result = self.manager.get_edge_cloud_zones()

    #     self.assertIsInstance(result, list)
    #     self.assertTrue(
    #         all("edgeCloudZoneId" in zone and "status" in zone
    #             for zone in result))

    #     # Optional: check for known zone
    #     known_zone = {
    #         "edgeCloudZoneId": "urn:ngsi-ld:Domain:NCSRD",
    #         "status": "functional"
    #     }
    #     self.assertIn(known_zone, result)

    # def test_onboard_app_success(self):
    #     '''
    #         Test if onboard_app returns a dictionary with appId
    #         Check if the appId is correct
    #     '''
    #     tosca_str = TOSCA_YAML_EXAMPLE

    #     app_manifest = {
    #         "serviceId": "urn:ngsi-ld:Service:cloud-edge-app",
    #         "tosca": tosca_str
    #     }

    #     result = self.manager.onboard_app(app_manifest)

    #     self.assertIsInstance(result, dict)
    #     self.assertIn("appId", result)
    #     self.assertEqual(result["appId"], "urn:ngsi-ld:Service:cloud-edge-app")

    # def test_undeploy_app_completes_successfully(self):
    #     '''
    #         Test if undeploy_app completes successfully
    #         Check if the appInstanceId is a string and starts with "urn:ngsi-ld:Service:"
    #     '''
    #     app_instance_id = "urn:ngsi-ld:Service:cloud-edge-app"
    #     self.manager.undeploy_app(app_instance_id)

    # def test_deploy_app_returns_app_instance_id(self):
    #     '''
    #         Test if deploy_app returns a dictionary with appInstanceId
    #         Check if the appInstanceId is a string and starts with "urn:ngsi-ld:Service:"
    #     '''
    #     app_id = "urn:ngsi-ld:Service:xai-service"
    #     app_zones = []  # Not used in current implementation

    #     result = self.manager.deploy_app(app_id, app_zones)

    #     self.assertIsInstance(result, dict)
    #     self.assertIn("appInstanceId", result)
    #     self.assertIsInstance(result["appInstanceId"], str)
    #     self.assertTrue(
    #         result["appInstanceId"].startswith("urn:ngsi-ld:Service:"))

    def test_get_edge_cloud_zones_details_structure(self):
        """
        Test if get_edge_cloud_zones_details returns a dictionary
        Check if the dictionary contains expected keys and values.
        Check if the values are of the expected types.
        """

        zone_id = "urn:ngsi-ld:Domain:NCSRD"

        # When
        result: Dict[str, Any] = self.manager.get_edge_cloud_zones_details(
            zone_id
        )  # <-- FIX HERE!

        # Then
        self.assertIsInstance(result, dict)
        self.assertIn("zoneId", result)
        self.assertIn("reservedComputeResources", result)
        self.assertIn("computeResourceQuotaLimits", result)
        self.assertIn("flavoursSupported", result)

        reserved_resources = result.get("reservedComputeResources", [])
        self.assertIsInstance(reserved_resources, list)

        for resource in reserved_resources:
            self.assertIsInstance(resource, dict)
            self.assertIn("cpuArchType", resource)
            self.assertIn("numCPU", resource)
            self.assertIn("memory", resource)

        quota_limits = result.get("computeResourceQuotaLimits", [])
        self.assertIsInstance(quota_limits, list)

        for limit in quota_limits:
            self.assertIsInstance(limit, dict)
            self.assertIn("cpuArchType", limit)
            self.assertIn("numCPU", limit)
            self.assertIn("memory", limit)

        flavours = result.get("flavoursSupported", [])
        self.assertIsInstance(flavours, list)

        for flavour in flavours:
            self.assertIsInstance(flavour, dict)
            self.assertIn("flavourId", flavour)
            self.assertIn("cpuArchType", flavour)
            self.assertIn("supportedOSTypes", flavour)
            self.assertIn("numCPU", flavour)
            self.assertIn("memorySize", flavour)
            self.assertIn("storageSize", flavour)

            supported_oses = flavour.get("supportedOSTypes", [])
            self.assertIsInstance(supported_oses, list)

            for os_type in supported_oses:
                self.assertIsInstance(os_type, dict)
                self.assertIn("architecture", os_type)
                self.assertIn("distribution", os_type)
                self.assertIn("version", os_type)
                self.assertIn("license", os_type)


if __name__ == "__main__":
    unittest.main()
