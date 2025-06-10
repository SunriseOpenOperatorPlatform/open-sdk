# -*- coding: utf-8 -*-
# This file defines the Pydantic models that represent the data structures (schemas)
# for the requests sent to and responses received from the Open5GS NEF API,
# specifically focusing on the APIs needed to support CAMARA QoD.

import ipaddress
from enum import Enum
from ipaddress import IPv4Address, IPv6Address
from typing import Annotated

from pydantic import AnyUrl, BaseModel, ConfigDict, Field, NonNegativeInt, RootModel
from pydantic_extra_types.mac_address import MacAddress


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
    reqQosMonParams: list[RequestedQosMonitoringParameter] | None = Field(
        None, min_length=1
    )
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
    qosReference: str | None = Field(
        None, description="Identifies a pre-defined QoS information"
    )
    altQoSReferences: list[str] | None = Field(
        None,
        description="Identifies an ordered list of pre-defined QoS information. The \
            lower the index of the array for a given entry, the higher the priority.",
        min_length=1,
    )
    ueIpv4Addr: ipaddress.IPv4Address | None = None
    ueIpv6Addr: ipaddress.IPv6Address | None = None
    macAddr: MacAddress | None = None
    usageThreshold: UsageThreshold | None = None
    sponsorInfo: SponsorInformation | None = None
    qosMonInfo: QosMonitoringInformationModel | None = None


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

    def add_flow_descriptor(self, flow_desriptor: str):
        self.trafficFilters = list()
        self.trafficFilters.append(
            FlowInfo(
                flowId=len(self.trafficFilters) + 1, flowDescriptions=[flow_desriptor]
            )
        )

    def add_traffic_route(self, dnai: str):
        self.trafficRoutes = list()
        self.trafficRoutes.append(TrafficRoute(dnai=dnai))

    def add_snssai(self, sst: int, sd: str = None):
        self.snssai = Snssai(sst=sst, sd=sd)


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
        Field(
            description="A list of single ports or port ranges on the application server"
        ),
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
