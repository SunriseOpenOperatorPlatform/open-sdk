# Contributors:
#   - Panagiotis Pavlidis (p.pavlidis@iit.demokritos.gr)
##

import pytest

from sunrise6g_opensdk.common.sdk import Sdk as sdkclient
from sunrise6g_opensdk.network.core.base_network_client import BaseNetworkClient
from sunrise6g_opensdk.network.core.common import CoreHttpError
from sunrise6g_opensdk.network.core.schemas import (
    AreaType,
    Device,
    Location,
    MonitoringEventSubscriptionRequest,
    Point,
    PointList,
    Polygon,
    RetrievalLocationRequest,
)

# --- Test config ---
client_specs = {
    "network": {
        "client_name": "open5gs",
        "base_url": "http://127.0.0.1:8000/",
        "scs_as_id": "af_1",
    }
}
clients = sdkclient.create_adapters_from(client_specs)
network_client: BaseNetworkClient = clients.get("network")


# Test full input data from Camara Payload
# {
#   "phoneNumber": "+1234567890",
#   "networkAccessIdentifier": "user123@example.com",
#   "ipv4Address": {
#     "publicAddress": "198.51.100.10",
#     "privateAddress": "10.0.0.1",
#     "publicPort": 12345
#   },
#   "ipv6Address": "2001:0db8:85a3:0000:0000:8a2e:0370:7334"
# }

camara_payload_input_data = RetrievalLocationRequest(device=Device(phoneNumber="+306912345678"))


# Sample output test data 3GPP MonitoringEventSubscription Request Payload
# {
#   "msisdn": "+306912345678",
#   "notificationDestination": "https://af.example.com/location_notifications",
#   "monitoringType": "LOCATION_REPORTING",
#   "locationType": "CURRENT_LOCATION"
# }

output_msisdn = camara_payload_input_data.device.phoneNumber.root.lstrip("+")
expected_3gpp_output_data = MonitoringEventSubscriptionRequest(
    msisdn=output_msisdn,
    notificationDestination="http://127.0.0.1:8001",
    monitoringType="LOCATION_REPORTING",
    locationType="LAST_KNOWN_LOCATION",
)


# Example:
#
# {
#     "lastLocationTime": "2025-06-23T20:47:22Z",
#     "area": {
#         "areaType": "POLYGON",
#         "boundary": [
#         {
#             "latitude": 37.9838,
#             "longitude": 23.7275
#         },
#         {
#             "latitude": 37.98,
#             "longitude": 23.75
#         },
#         {
#             "latitude": 37.97,
#             "longitude": 23.73
#         },
#         {   "latitude": 37.975,
#             "longtitude": 23.71
#         }
#         ]
#     }
# }

point1 = Point(latitude=37.9838, longitude=23.7275)
point2 = Point(latitude=37.98, longitude=23.75)
point3 = Point(latitude=37.97, longitude=23.73)
point4 = Point(latitude=37.975, longitude=23.71)
point_list = PointList(root=[point1, point2, point3, point4])

polygon_area = Polygon(areaType=AreaType.polygon, boundary=point_list)

expected_camara_output_data = Location(
    lastLocationTime="2025-06-23T20:47:22Z",
    area=polygon_area,
)


# --- TEST CASES ---


def test_camara_tf_3gpp_event() -> None:
    actual_result = network_client._build_monitoring_event_subscription(
        retrieve_location_request=camara_payload_input_data
    )
    assert (
        actual_result == expected_3gpp_output_data
    ), f"Expected actual_result ({actual_result}) \n to be equal to expected_result ({expected_3gpp_output_data}), but they were not."


def test_create_monitoring_event():
    try:
        actual_result = network_client.create_monitoring_event_subscription(
            retrieve_location_request=camara_payload_input_data
        )
        assert (
            actual_result == expected_camara_output_data
        ), f"Expected actual_result ({actual_result}) \n to be equal to expected_result ({expected_camara_output_data}), but they were not."
    except CoreHttpError as e:
        pytest.fail(f"Failed to retrieve event report: {e}")
