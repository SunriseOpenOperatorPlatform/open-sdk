from typing import List, Literal, Optional

from pydantic import BaseModel, Field, HttpUrl, RootModel

# ---------------------------
# FederationManagement
# ---------------------------


class ZoneDetails(BaseModel):
    zoneId: str
    geolocation: Optional[str] = None
    geographyDetails: str


class ZonesList(RootModel[List[ZoneDetails]]):
    pass


# ---------------------------
# AvailabilityZoneInfoSynchronization
# ---------------------------


class HugePage(BaseModel):
    pageSize: str
    number: int


class GpuInfo(BaseModel):
    gpuVendorType: Literal["GPU_PROVIDER_NVIDIA", "GPU_PROVIDER_AMD"]
    gpuModeName: str
    gpuMemory: int
    numGPU: int


class ComputeResourceInfo(BaseModel):
    cpuArchType: Literal["ISA_X86", "ISA_X86_64", "ISA_ARM_64"]
    numCPU: int
    memory: int
    diskStorage: Optional[int] = None
    gpu: Optional[List[GpuInfo]] = None
    vpu: Optional[int] = None
    fpga: Optional[int] = None
    hugepages: Optional[List[HugePage]] = None
    cpuExclusivity: Optional[bool] = None


class OSType(BaseModel):
    architecture: Literal["x86_64", "x86"]
    distribution: Literal["RHEL", "UBUNTU", "COREOS", "FEDORA", "WINDOWS", "OTHER"]
    version: Literal[
        "OS_VERSION_UBUNTU_2204_LTS",
        "OS_VERSION_RHEL_8",
        "OS_VERSION_RHEL_7",
        "OS_VERSION_DEBIAN_11",
        "OS_VERSION_COREOS_STABLE",
        "OS_MS_WINDOWS_2012_R2",
        "OTHER",
    ]
    license: Literal["OS_LICENSE_TYPE_FREE", "OS_LICENSE_TYPE_ON_DEMAND", "NOT_SPECIFIED"]


class Flavour(BaseModel):
    flavourId: str
    cpuArchType: Literal["ISA_X86", "ISA_X86_64", "ISA_ARM_64"]
    supportedOSTypes: List[OSType] = Field(..., min_items=1)
    numCPU: int
    memorySize: int
    storageSize: int
    gpu: Optional[List[GpuInfo]] = None
    fpga: Optional[List[str]] = None
    vpu: Optional[List[str]] = None
    hugepages: Optional[List[HugePage]] = None
    cpuExclusivity: Optional[List[str]] = None


class NetworkResources(BaseModel):
    egressBandWidth: int
    dedicatedNIC: int
    supportSriov: bool
    supportDPDK: bool


class LatencyRange(BaseModel):
    minLatency: int = Field(..., ge=1)
    maxLatency: int


class JitterRange(BaseModel):
    minJitter: int = Field(..., ge=1)
    maxJitter: int


class ThroughputRange(BaseModel):
    minThroughput: int = Field(..., ge=1)
    maxThroughput: int


class ZoneServiceLevelObjsInfo(BaseModel):
    latencyRanges: LatencyRange
    jitterRanges: JitterRange
    throughputRanges: ThroughputRange


class ZoneRegisteredData(BaseModel):
    zoneId: str
    reservedComputeResources: List[ComputeResourceInfo] = Field(..., min_items=1)
    computeResourceQuotaLimits: List[ComputeResourceInfo] = Field(..., min_items=1)
    flavoursSupported: List[Flavour] = Field(..., min_items=1)
    networkResources: Optional[NetworkResources] = None
    zoneServiceLevelObjsInfo: Optional[ZoneServiceLevelObjsInfo] = None


class ZoneRegisteredDataList(RootModel[List[ZoneRegisteredData]]):
    pass


# ---------------------------
# ArtefactManagement
# ---------------------------


class ArtefactRepoLocation(BaseModel):
    repoURL: HttpUrl
    userName: Optional[str] = None
    password: Optional[str] = None
    token: Optional[str] = None


class Artefact(BaseModel):
    artefactId: str
    appProviderId: Optional[str] = None
    artefactName: str
    artefactDescription: Optional[str] = None
    artefactVersionInfo: str
    artefactVirtType: Literal["VM_TYPE", "CONTAINER_TYPE"]
    artefactFileName: Optional[str] = None
    artefactFileFormat: Optional[Literal["ZIP", "TAR", "TEXT", "TARGZ"]] = None
    artefactDescriptorType: Literal["HELM", "TERRAFORM", "ANSIBLE", "SHELL", "COMPONENTSPEC"]
    repoType: Optional[Literal["PRIVATEREPO", "PUBLICREPO", "UPLOAD"]] = None
    artefactRepoLocation: Optional[ArtefactRepoLocation] = None


# ---------------------------
# ApplicationOnboardingManagement
# ---------------------------


class AppDeploymentZone(BaseModel):
    countryCode: str
    zoneInfo: str


class AppMetaData(BaseModel):
    appName: str
    version: str
    appDescription: Optional[str] = None
    mobilitySupport: bool = False
    accessToken: str
    category: Optional[
        Literal[
            "IOT",
            "HEALTH_CARE",
            "GAMING",
            "VIRTUAL_REALITY",
            "SOCIALIZING",
            "SURVEILLANCE",
            "ENTERTAINMENT",
            "CONNECTIVITY",
            "PRODUCTIVITY",
            "SECURITY",
            "INDUSTRIAL",
            "EDUCATION",
            "OTHERS",
        ]
    ] = None


class AppQoSProfile(BaseModel):
    latencyConstraints: Literal["NONE", "LOW", "ULTRALOW"]
    bandwidthRequired: int = Field(..., ge=1)
    multiUserClients: Literal["APP_TYPE_SINGLE_USER", "APP_TYPE_MULTI_USER"]
    noOfUsersPerAppInst: int = 1
    appProvisioning: bool = True


class AppComponentSpec(BaseModel):
    serviceNameNB: str
    serviceNameEW: str
    componentName: str
    artefactId: str


class ApplicationModel(BaseModel):
    appId: str
    appProviderId: str
    appDeploymentZones: List[AppDeploymentZone] = Field(..., min_length=1)
    appMetaData: AppMetaData
    appQoSProfile: AppQoSProfile
    appComponentSpecs: List[AppComponentSpec] = Field(..., min_length=1)
    onboardStatusInfo: Literal["PENDING", "ONBOARDED", "DEBOARDING", "REMOVED", "FAILED"]


# ---------------------------
# ApplicationDeploymentManagement
# ---------------------------


class AppInstance(BaseModel):
    zoneId: str
    appInstIdentifier: str


class AppInstanceStatus(BaseModel):
    appInstanceState: Literal["PENDING", "READY", "FAILED", "TERMINATING", "DEPLOYED"]
    accesspointInfo: List[dict]


class ZoneIdentifier(BaseModel):
    zoneId: str
    appInstanceInfo: List[dict]


class ZoneIdentifierList(RootModel[List[ZoneIdentifier]]):
    pass
