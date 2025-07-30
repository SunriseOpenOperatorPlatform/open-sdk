# -*- coding: utf-8 -*-
# This file defines the Pydantic models that represent the data structures (schemas)
# for the requests sent to and responses received from the Open5GS NEF API,
# specifically focusing on the APIs needed to support CAMARA QoD.

import ipaddress
from datetime import datetime
from enum import Enum
from ipaddress import IPv4Address, IPv6Address
from typing import Annotated, Literal
from uuid import UUID

from pydantic import (
    AnyHttpUrl,
    AnyUrl,
    BaseModel,
    ConfigDict,
    Field,
    NonNegativeInt,
    RootModel,
)
from pydantic_extra_types.mac_address import MacAddress

from sunrise6g_opensdk.logger import setup_logger
from sunrise6g_opensdk.network.adapters.errors import NetworkPlatformError

log = setup_logger(__name__)


class FlowDirection(Enum):
    """
    DOWNLINK: The corresponding filter applies for traffic to the UE.
    UPLINK: The corresponding filter applies for traffic from the UE.
    BIDIRECTIONAL: The corresponding filter applies for traffic both to and from the UE.
    UNSPECIFIED: The corresponding filter applies for traffic to the UE (downlink), but
    has no specific direction declared. The service data flow detection shall apply the
    filter for uplink traffic as if the filter was bidirectional. The PCF shall not use
    the value UNSPECIFIED in filters created by the network in NW-initiated procedures.
    The PCF shall only include the value UNSPECIFIED in filters in UE-initiated
    procedures if the same value is received from the SMF.
    """

    DOWNLINK = "DOWNLINK"
    UPLINK = "UPLINK"
    BIDIRECTIONAL = "BIDIRECTIONAL"
    UNSPECIFIED = "UNSPECIFIED"


class RequestedQosMonitoringParameter(Enum):
    DOWNLINK = "DOWNLINK"
    UPLINK = "UPLINK"
    ROUND_TRIP = "ROUND_TRIP"


class ReportingFrequency(Enum):
    EVENT_TRIGGERED = "EVENT_TRIGGERED"
    PERIODIC = "PERIODIC"
    SESSION_RELEASE = "SESSION_RELEASE"


Uinteger = Annotated[int, Field(ge=0)]


class DurationSec(RootModel[NonNegativeInt]):
    root: NonNegativeInt = Field(
        ...,
        description="Unsigned integer identifying a period of time in units of \
        seconds.",
    )


class Volume(RootModel[NonNegativeInt]):
    root: NonNegativeInt = Field(
        ..., description="Unsigned integer identifying a volume in units of bytes."
    )


class SupportedFeatures(RootModel[str]):
    root: str = Field(
        ...,
        pattern=r"^[A-Fa-f0-9]*$",
        description="Hexadecimal string representing supported features.",
    )


class Link(RootModel[str]):
    root: str = Field(
        ...,
        description="String formatted according to IETF RFC 3986 identifying a \
                     referenced resource.",
    )


class FlowDescriptionModel(RootModel[str]):
    root: str = Field(..., description="Defines a packet filter of an IP flow.")


class EthFlowDescription(BaseModel):
    destMacAddr: MacAddress | None = None
    ethType: str
    fDesc: FlowDescriptionModel | None = None
    fDir: FlowDirection | None = None
    sourceMacAddr: MacAddress | None = None
    vlanTags: list[str] | None = Field(None, max_length=2, min_length=1)
    srcMacAddrEnd: MacAddress | None = None
    destMacAddrEnd: MacAddress | None = None


class UsageThreshold(BaseModel):
    duration: DurationSec | None = None
    totalVolume: Volume | None = None
    downlinkVolume: Volume | None = None
    uplinkVolume: Volume | None = None


class SponsorInformation(BaseModel):
    sponsorId: str = Field(..., description="It indicates Sponsor ID.")
    aspId: str = Field(..., description="It indicates Application Service Provider ID.")


class QosMonitoringInformationModel(BaseModel):
    reqQosMonParams: list[RequestedQosMonitoringParameter] | None = Field(None, min_length=1)
    repFreqs: list[ReportingFrequency] | None = Field(None, min_length=1)
    repThreshDl: Uinteger | None = None
    repThreshUl: Uinteger | None = None
    repThreshRp: Uinteger | None = None
    waitTime: int | None = None
    repPeriod: int | None = None


class FlowInfo(BaseModel):
    flowId: int = Field(..., description="Indicates the IP flow.")
    flowDescriptions: list[str] | None = Field(
        None,
        description="Indicates the packet filters of the IP flow. Refer to subclause \
            5.3.8 of 3GPP TS 29.214 for encoding. It shall contain UL and/or DL IP \
            flow description.",
        max_length=2,
        min_length=1,
    )


class Snssai(BaseModel):
    sst: int = Field(default=1)
    sd: str = Field(default="FFFFFF")


class AsSessionWithQoSSubscription(BaseModel):
    model_config = ConfigDict(serialize_by_alias=True)
    self_: Link | None = Field(None, alias="self")
    supportedFeatures: SupportedFeatures | None = None
    notificationDestination: Link
    flowInfo: list[FlowInfo] | None = Field(
        None, description="Describe the data flow which requires QoS.", min_length=1
    )
    ethFlowInfo: list[EthFlowDescription] | None = Field(
        None, description="Identifies Ethernet packet flows.", min_length=1
    )
    qosReference: str | None = Field(None, description="Identifies a pre-defined QoS information")
    altQoSReferences: list[str] | None = Field(
        None,
        description="Identifies an ordered list of pre-defined QoS information. The \
            lower the index of the array for a given entry, the higher the priority.",
        min_length=1,
    )
    ueIpv4Addr: ipaddress.IPv4Address | None = None
    ueIpv6Addr: ipaddress.IPv6Address | None = None
    macAddr: MacAddress | None = None
    snssai: Snssai | None = None
    dnn: str | None = None
    usageThreshold: UsageThreshold | None = None
    sponsorInfo: SponsorInformation | None = None
    qosMonInfo: QosMonitoringInformationModel | None = None

    @property
    def subscription_id(self) -> str:
        """
        Returns the subscription ID, which is the same as the self link.
        """
        subscription_id = self.self_.root.split("/")[-1] if self.self_.root else None
        if not subscription_id:
            log.error("Failed to retrieve QoS session ID from response")
            raise NetworkPlatformError("QoS session ID not found in response")
        return subscription_id


class SourceTrafficFilters(BaseModel):
    sourcePort: int


class DestinationTrafficFilters(BaseModel):
    destinationPort: int
    destinationProtocol: str


class TrafficRoute(BaseModel):
    dnai: str


class TrafficInfluSub(BaseModel):  # Replace with a meaningful name
    afServiceId: str | None = None
    afAppId: str
    dnn: str | None = None
    snssai: Snssai | None = None
    trafficFilters: list[FlowInfo] | None = Field(
        None,
        description="Describe the data flow which requires Traffic Influence.",
        min_length=1,
    )
    ipv4Addr: str | None = None
    ipv6Addr: str | None = None

    notificationDestination: str
    trafficRoutes: list[TrafficRoute] | None = Field(
        None,
        description="Describe the list of DNAIs to reach the destination",
        min_length=1,
    )
    suppFeat: str | None = None

    def add_flow_descriptor(self, flow_descriptor: str):
        self.trafficFilters = list()
        self.trafficFilters.append(
            FlowInfo(flowId=len(self.trafficFilters) + 1, flowDescriptions=[flow_descriptor])
        )

    def add_traffic_route(self, dnai: str):
        self.trafficRoutes = list()
        self.trafficRoutes.append(TrafficRoute(dnai=dnai))

    def add_snssai(self, sst: int, sd: str = None):
        self.snssai = Snssai(sst=sst, sd=sd)


# Monitoring Event API


class DurationMin(BaseModel):
    duration: int = Field(
        0,
        description="Unsigned integer identifying a period of time in units of minutes",
        ge=0,
    )


class PlmnId(BaseModel):
    mcc: str = Field(
        ...,
        description="String encoding a Mobile Country Code, comprising of 3 digits.",
    )
    mnc: str = Field(
        ...,
        description="String encoding a Mobile Network Code, comprising of 2 or 3 digits.",
    )


# The enumeration Accuracy represents a desired granularity of accuracy of the requested location information.
class Accuracy(str, Enum):
    cgi_ecgi = "CGI_ECGI"  # The AF requests to be notified using cell level location accuracy.
    ta_ra = "TA_RA"  # The AF requests to be notified using TA/RA level location accuracy.
    geo_area = "GEO_AREA"  # The AF requests to be notified using the geographical area accuracy.
    civic_addr = (
        "CIVIC_ADDR"  # The AF requests to be notified using the civic address accuracy. #EDGEAPP
    )


# If locationType set to "LAST_KNOWN_LOCATION", the monitoring event request from AF shall be only for one-time monitoring request
class LocationType(str, Enum):
    CURRENT_LOCATION = "CURRENT_LOCATION"  # The AF requests to be notified for current location.
    LAST_KNOWN = "LAST_KNOWN_LOCATION"  # The AF requests to be notified for last known location.


# This data type represents a monitoring event type.
class MonitoringType(str, Enum):
    LOCATION_REPORTING = "LOCATION_REPORTING"


class LocationFailureCause(str, Enum):
    position_denied = "POSITIONING_DENIED"  # Positioning is denied.
    unsupported_by_ue = "UNSUPPORTED_BY_UE"  # Positioning is not supported by UE.
    not_registered_ue = "NOT_REGISTERED_UE"  # UE is not registered.
    unspecified = "UNSPECIFIED"  # Unspecified cause.


class GeographicalCoordinates(BaseModel):
    lon: float = Field(..., description="Longitude coordinate.")
    lat: float = Field(..., description="Latitude coordinate.")


class PointListNef(BaseModel):
    geographical_coords: list[GeographicalCoordinates] = Field(
        ...,
        description="List of geographical coordinates defining the points.",
        min_length=3,
        max_length=15,
    )


class NefPolygon(BaseModel):
    point_list: PointListNef = Field(..., description="List of points defining the polygon.")


class GeographicArea(BaseModel):
    polygon: NefPolygon | None = Field(None, description="Identifies a polygonal geographic area.")


# This data type represents the user location information which is sent from the NEF to the AF.
class LocationInfo(BaseModel):
    ageOfLocationInfo: DurationMin | None = Field(
        None,
        description="Indicates the elapsed time since the last network contact of the UE.",
    )
    cellId: str | None = Field(None, description="Cell ID where the UE is located.")
    trackingAreaId: str | None = Field(None, description="TrackingArea ID where the UE is located.")
    enodeBId: str | None = Field(None, description="eNodeB ID where the UE is located.")
    routingAreaId: str | None = Field(None, description="Routing Area ID where the UE is located")
    plmnId: PlmnId | None = Field(None, description="PLMN ID where the UE is located.")
    twanId: str | None = Field(None, description="TWAN ID where the UE is located.")
    geographicArea: GeographicArea | None = Field(
        None,
        description="Identifies a geographic area of the user where the UE is located.",
    )


class MonitoringEventSubscriptionRequest(BaseModel):
    accuracy: Accuracy | None = Field(
        None,
        description="Accuracy represents a desired granularity of accuracy of the requested location information.",
    )
    externalId: str | None = Field(
        None, description="Identifies a user clause 4.6.2 TS 23.682 (optional)"
    )
    msisdn: str | None = Field(
        None,
        description="Identifies the MS internal PSTN/ISDN number allocated for a UE.",
    )
    ipv4Addr: IPv4Address | None = Field(None, description="Identifies the Ipv4 address.")
    ipv6Addr: IPv6Address | None = Field(None, description="Identifies the Ipv6 address.")
    notificationDestination: AnyHttpUrl = Field(
        ...,
        description="URI of a notification destination that the T8 message shall be delivered to.",
    )
    monitoringType: MonitoringType = Field(
        ..., description="Enumeration of monitoring type. Refer to clause 5.3.2.4.3."
    )
    maximumNumberOfReports: int | None = Field(
        None,
        description="Identifies the maximum number of event reports to be generated by the AMF to the NEF and then the AF.",
    )
    monitorExpireTime: datetime | None = Field(
        None,
        description="Identifies the absolute time at which the related monitoring event request is considered to expire.",
    )
    locationType: LocationType | None = Field(
        None,
        description="Indicates whether the request is for Current Location, Initial Location, or Last Known Location.",
    )
    repPeriod: DurationSec | None = Field(
        None, description="Identifies the periodic time for the event reports."
    )
    minimumReportInterval: DurationSec | None = Field(
        None,
        description="identifies a minimum time interval between Location Reporting notifications",
    )


# This data type represents a monitoring event notification which is sent from the NEF to the AF.
class MonitoringEventReport(BaseModel):
    externalId: str | None = Field(None, description="Identifies a user, clause 4.6.2 TS 23.682")
    msisdn: str | None = Field(
        None,
        description="Identifies the MS internal PSTN/ISDN number allocated for a UE.",
    )
    locationInfo: LocationInfo | None = Field(
        None, description="Indicates the user location related information."
    )
    locFailureCause: LocationFailureCause | None = Field(
        None, description="Indicates the location positioning failure cause."
    )
    monitoringType: MonitoringType = Field(
        ...,
        description="Identifies the type of monitoring as defined in clause 5.3.2.4.3.",
    )
    eventTime: datetime | None = Field(
        None,
        description="Identifies when the event is detected or received. Shall be included for each group of UEs.",
    )


# This data type represents a monitoring notification which is sent from the NEF to the AF.
class MonitoringNotification(BaseModel):
    subscription: AnyHttpUrl = Field(
        ...,
        description="Link to the subscription resource to which this notification is related.",
    )
    monitoringEventReports: list[MonitoringEventReport] | None = Field(
        None,
        description="Each element identifies a monitoring event report (optional).",
    )
    cancelInd: bool | None = Field(
        False,
        description="Indicates whether to request to cancel the corresponding monitoring subscription. Set to false or omitted otherwise.",
    )


###############################################################
###############################################################
# CAMARA Models


class PhoneNumber(RootModel[str]):
    root: Annotated[
        str,
        Field(
            description="A public identifier addressing a telephone subscription. In mobile networks it corresponds to the MSISDN (Mobile Station International Subscriber Directory Number). In order to be globally unique it has to be formatted in international format, according to E.164 standard, prefixed with '+'.",
            examples=["+123456789"],
            pattern="^\\+[1-9][0-9]{4,14}$",
        ),
    ]


class NetworkAccessIdentifier(RootModel[str]):
    root: Annotated[
        str,
        Field(
            description="A public identifier addressing a subscription in a mobile network. In 3GPP terminology, it corresponds to the GPSI formatted with the External Identifier ({Local Identifier}@{Domain Identifier}). Unlike the telephone number, the network access identifier is not subjected to portability ruling in force, and is individually managed by each operator.",
            examples=["123456789@domain.com"],
        ),
    ]


class SingleIpv4Addr(RootModel[IPv4Address]):
    root: Annotated[
        IPv4Address,
        Field(
            description="A single IPv4 address with no subnet mask",
            examples=["203.0.113.0"],
        ),
    ]


class Port(RootModel[int]):
    root: Annotated[int, Field(description="TCP or UDP port number", ge=0, le=65535)]


class DeviceIpv4Addr1(BaseModel):
    publicAddress: SingleIpv4Addr
    privateAddress: SingleIpv4Addr
    publicPort: Port | None = None


class DeviceIpv4Addr2(BaseModel):
    publicAddress: SingleIpv4Addr
    privateAddress: SingleIpv4Addr | None = None
    publicPort: Port


class DeviceIpv4Addr(RootModel[DeviceIpv4Addr1 | DeviceIpv4Addr2]):
    root: Annotated[
        DeviceIpv4Addr1 | DeviceIpv4Addr2,
        Field(
            description="The device should be identified by either the public (observed) IP address and port as seen by the application server, or the private (local) and any public (observed) IP addresses in use by the device (this information can be obtained by various means, for example from some DNS servers).\n\nIf the allocated and observed IP addresses are the same (i.e. NAT is not in use) then  the same address should be specified for both publicAddress and privateAddress.\n\nIf NAT64 is in use, the device should be identified by its publicAddress and publicPort, or separately by its allocated IPv6 address (field ipv6Address of the Device object)\n\nIn all cases, publicAddress must be specified, along with at least one of either privateAddress or publicPort, dependent upon which is known. In general, mobile devices cannot be identified by their public IPv4 address alone.\n",
            examples=[{"publicAddress": "203.0.113.0", "publicPort": 59765}],
        ),
    ]


class DeviceIpv6Address(RootModel[IPv6Address]):
    root: Annotated[
        IPv6Address,
        Field(
            description="The device should be identified by the observed IPv6 address, or by any single IPv6 address from within the subnet allocated to the device (e.g. adding ::0 to the /64 prefix).\n\nThe session shall apply to all IP flows between the device subnet and the specified application server, unless further restricted by the optional parameters devicePorts or applicationServerPorts.\n",
            examples=["2001:db8:85a3:8d3:1319:8a2e:370:7344"],
        ),
    ]


class Device(BaseModel):
    phoneNumber: PhoneNumber | None = None
    networkAccessIdentifier: NetworkAccessIdentifier | None = None
    ipv4Address: DeviceIpv4Addr | None = None
    ipv6Address: DeviceIpv6Address | None = None


class RetrievalLocationRequest(BaseModel):
    """
    Request to retrieve the location of a device. Device is not required when using a 3-legged access token.
    """

    device: Annotated[
        Device | None,
        Field(None, description="End-user device able to connect to a mobile network."),
    ]
    maxAge: Annotated[
        int | None,
        Field(
            None,
            description="Maximum age of the location information which is accepted for the location retrieval (in seconds).",
        ),
    ]
    maxSurface: Annotated[
        int | None,
        Field(
            None,
            description="Maximum surface in square meters which is accepted by the client for the location retrieval.",
            ge=1,
            examples=[1000000],
        ),
    ]


class AreaType(str, Enum):
    circle = "CIRCLE"  # The area is defined as a circle.
    polygon = "POLYGON"  # The area is defined as a polygon.


class Point(BaseModel):
    latitude: Annotated[
        float,
        Field(
            description="Latitude component of a location.",
            examples=["50.735851"],
            ge=-90,
            le=90,
        ),
    ]
    longitude: Annotated[
        float,
        Field(
            ...,
            description="Longitude component of location.",
            examples=["7.10066"],
            ge=-180,
            le=180,
        ),
    ]


class PointList(
    RootModel[
        Annotated[
            list[Point],
            Field(
                min_length=3,
                max_length=15,
                description="List of points defining the area.",
            ),
        ]
    ]
):
    pass


class Circle(BaseModel):
    areaType: Literal[AreaType.circle]
    center: Annotated[Point, Field(description="Center point of the circle.")]
    radius: Annotated[float, Field(description="Radius of the circle.", ge=1)]


class Polygon(BaseModel):
    areaType: Literal[AreaType.polygon]
    boundary: Annotated[PointList, Field(description="List of points defining the polygon.")]


Area = Annotated[Circle | Polygon, Field(discriminator="areaType")]


class LastLocationTime(
    RootModel[
        Annotated[
            datetime,
            Field(
                description="Last date and time when the device was localized.",
                examples="2023-09-07T10:40:52Z",
            ),
        ]
    ]
):
    pass


class Location(BaseModel):
    lastLocationTime: Annotated[LastLocationTime, Field(description="Last known location time.")]
    area: Annotated[Area, Field(description="Geographical area of the location.")]


class ApplicationServerIpv4Address(RootModel[str]):
    root: Annotated[
        str,
        Field(
            description="IPv4 address may be specified in form <address/mask> as:\n  - address - an IPv4 number in dotted-quad form 1.2.3.4. Only this exact IP number will match the flow control rule.\n  - address/mask - an IP number as above with a mask width of the form 1.2.3.4/24.\n    In this case, all IP numbers from 1.2.3.0 to 1.2.3.255 will match. The bit width MUST be valid for the IP version.\n",
            examples=["198.51.100.0/24"],
        ),
    ]


class ApplicationServerIpv6Address(RootModel[str]):
    root: Annotated[
        str,
        Field(
            description="IPv6 address may be specified in form <address/mask> as:\n  - address - The /128 subnet is optional for single addresses:\n    - 2001:db8:85a3:8d3:1319:8a2e:370:7344\n    - 2001:db8:85a3:8d3:1319:8a2e:370:7344/128\n  - address/mask - an IP v6 number with a mask:\n    - 2001:db8:85a3:8d3::0/64\n    - 2001:db8:85a3:8d3::/64\n",
            examples=["2001:db8:85a3:8d3:1319:8a2e:370:7344"],
        ),
    ]


class ApplicationServer(BaseModel):
    ipv4Address: ApplicationServerIpv4Address | None = None
    ipv6Address: ApplicationServerIpv6Address | None = None


class Range(BaseModel):
    from_: Annotated[Port, Field(alias="from")]
    to: Port


class PortsSpec(BaseModel):
    ranges: Annotated[
        list[Range] | None, Field(description="Range of TCP or UDP ports", min_length=1)
    ] = None
    ports: Annotated[
        list[Port] | None, Field(description="Array of TCP or UDP ports", min_length=1)
    ] = None


class QosProfileName(RootModel[str]):
    root: Annotated[
        str,
        Field(
            description="A unique name for identifying a specific QoS profile.\nThis may follow different formats depending on the API provider implementation.\nSome options addresses:\n  - A UUID style string\n  - Support for predefined profiles QOS_S, QOS_M, QOS_L, and QOS_E\n  - A searchable descriptive name\nThe set of QoS Profiles that an API provider is offering may be retrieved by means of the QoS Profile API (qos-profile) or agreed on onboarding time.\n",
            examples=["voice"],
            max_length=256,
            min_length=3,
            pattern="^[a-zA-Z0-9_.-]+$",
        ),
    ]


class CredentialType(Enum):
    PLAIN = "PLAIN"
    ACCESSTOKEN = "ACCESSTOKEN"
    REFRESHTOKEN = "REFRESHTOKEN"


class SinkCredential(BaseModel):
    credentialType: Annotated[
        CredentialType,
        Field(
            description="The type of the credential.\nNote: Type of the credential - MUST be set to ACCESSTOKEN for now\n"
        ),
    ]


class NotificationSink(BaseModel):
    sink: str | None
    sinkCredential: SinkCredential | None


class BaseSessionInfo(BaseModel):
    device: Device | None = None
    applicationServer: ApplicationServer
    devicePorts: Annotated[
        PortsSpec | None,
        Field(
            description="The ports used locally by the device for flows to which the requested QoS profile should apply. If omitted, then the qosProfile will apply to all flows between the device and the specified application server address and ports"
        ),
    ] = None
    applicationServerPorts: Annotated[
        PortsSpec | None,
        Field(description="A list of single ports or port ranges on the application server"),
    ] = None
    qosProfile: QosProfileName
    sink: Annotated[
        AnyUrl | None,
        Field(
            description="The address to which events about all status changes of the session (e.g. session termination) shall be delivered using the selected protocol.",
            examples=["https://endpoint.example.com/sink"],
        ),
    ] = None
    sinkCredential: Annotated[
        SinkCredential | None,
        Field(
            description="A sink credential provides authentication or authorization information necessary to enable delivery of events to a target."
        ),
    ] = None


class CreateSession(BaseSessionInfo):
    duration: Annotated[
        int,
        Field(
            description="Requested session duration in seconds. Value may be explicitly limited for the QoS profile, as specified in the Qos Profile (see qos-profile API). Implementations can grant the requested session duration or set a different duration, based on network policies or conditions.\n",
            examples=[3600],
            ge=1,
        ),
    ]


class SessionId(RootModel[UUID]):
    root: Annotated[UUID, Field(description="Session ID in UUID format")]


class QosStatus(Enum):
    REQUESTED = "REQUESTED"
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"


class StatusInfo(Enum):
    DURATION_EXPIRED = "DURATION_EXPIRED"
    NETWORK_TERMINATED = "NETWORK_TERMINATED"
    DELETE_REQUESTED = "DELETE_REQUESTED"


class SessionInfo(BaseSessionInfo):
    sessionId: SessionId
    duration: Annotated[
        int,
        Field(
            description='Session duration in seconds. Implementations can grant the requested session duration or set a different duration, based on network policies or conditions.\n- When `qosStatus` is "REQUESTED", the value is the duration to be scheduled, granted by the implementation.\n- When `qosStatus` is AVAILABLE", the value is the overall duration since `startedAt. When the session is extended, the value is the new overall duration of the session.\n- When `qosStatus` is "UNAVAILABLE", the value is the overall effective duration since `startedAt` until the session was terminated.\n',
            examples=[3600],
            ge=1,
        ),
    ]
    startedAt: Annotated[
        datetime | None,
        Field(
            description='Date and time when the QoS status became "AVAILABLE". Not to be returned when `qosStatus` is "REQUESTED". Format must follow RFC 3339 and must indicate time zone (UTC or local).',
            examples=["2024-06-01T12:00:00Z"],
        ),
    ] = None
    expiresAt: Annotated[
        datetime | None,
        Field(
            description='Date and time of the QoS session expiration. Format must follow RFC 3339 and must indicate time zone (UTC or local).\n- When `qosStatus` is "AVAILABLE", it is the limit time when the session is scheduled to finnish, if not terminated by other means.\n- When `qosStatus` is "UNAVAILABLE", it is the time when the session was terminated.\n- Not to be returned when `qosStatus` is "REQUESTED".\nWhen the session is extended, the value is the new expiration time of the session.\n',
            examples=["2024-06-01T13:00:00Z"],
        ),
    ] = None
    qosStatus: QosStatus
    statusInfo: StatusInfo | None = None


class CreateTrafficInfluence(BaseModel):
    trafficInfluenceID: str | None = None
    apiConsumerId: str | None = None
    appId: str
    appInstanceId: str
    edgeCloudRegion: str | None = None
    edgeCloudZoneId: str | None = None
    sourceTrafficFilters: SourceTrafficFilters | None = None
    destinationTrafficFilters: DestinationTrafficFilters | None = None
    notificationUri: str | None = None
    notificationAuthToken: str | None = None
    device: Device
    notificationSink: NotificationSink | None = None

    def retrieve_ue_ipv4(self):
        if self.device is not None and self.device.ipv4Address is not None:
            return self.device.ipv4Address.root.privateAddress.root
        else:
            raise KeyError("device.ipv4Address.publicAddress")

    def add_ue_ipv4(self, ipv4: str):
        if self.device is None:
            self.device = Device()
        if self.device.ipv4Address is None:
            self.device.ipv4Address = DeviceIpv4Addr(publicAddress=ipv4)
