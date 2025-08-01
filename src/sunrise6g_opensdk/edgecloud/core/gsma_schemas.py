from typing import List, Literal, Optional

from pydantic import BaseModel, Field, RootModel

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


# ---------------------------
# ApplicationOnboardingManagement
# ---------------------------


# ---------------------------
# ApplicationDeploymentManagement
# ---------------------------
