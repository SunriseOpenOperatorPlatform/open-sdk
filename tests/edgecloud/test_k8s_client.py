import unittest


from sunrise6g_opensdk.edgecloud.clients.piedge.client import EdgeApplicationManager


class TestK8sEdgeApplicationManager(unittest.TestCase):

    def setUp(self):
        kwargs = {
            "PLATFORM_PROVIDER": "ICOM",
            "KUBERNETES_MASTER_TOKEN": "T3FRNnNVK25FY3I5ZHlNYmxrSEFpd2VPcW5WTlliTnRVNVo3bitNY1B3az0K",
            "KUBERNETES_MASTER_PORT": "16443",
            "EMP_STORAGE_URI": "mongodb://mongopiedge:27017",
            "KUBERNETES_USERNAME": "user",
        }
        self.manager = EdgeApplicationManager(base_url="146.124.106.200", **kwargs)

    def test_edge_cloud_zones_retrieval(self):

        edge_cloud_zones = self.manager.get_edge_cloud_zones()
        self.assertTrue(edge_cloud_zones)
        self.assertIsInstance(edge_cloud_zones, list)
