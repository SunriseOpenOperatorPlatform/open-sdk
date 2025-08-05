#!/usr/bin/env python3
# -*- coding: utf-8 -*-
##
# This file is part of the Open SDK
#
# Contributors:
#   - Sergio Giménez (sergio.gimenez@i2cat.net)
#   - César Cajas (cesar.cajas@i2cat.net)
#   - Adrián Pino Martínez (adrian.pino@i2cat.net)
##

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

# Zone and Flavour


class ZoneInfoRef(BaseModel):
    flavourId: str
    zoneId: str


class ZoneInfo(BaseModel):
    zoneId: str
    geographyDetails: Optional[str] = None
    geolocation: Optional[str] = None
    computeResourceQuotaLimits: Optional[List[dict]] = None
    flavoursSupported: Optional[List["Flavour"]] = None
    networkResources: Optional[dict] = None
    reservedComputeResources: Optional[List[dict]] = None
    zoneServiceLevelObjsInfo: Optional[dict] = None


class Hugepages(BaseModel):
    number: int = Field(default=0, description="Number of hugepages")
    pageSize: str = Field(default="2MB", description="Size of hugepages")


class GPU(BaseModel):
    gpuMemory: int = Field(default=0, description="GPU memory in MB")
    gpuModeName: str = Field(default="", description="GPU mode name")
    gpuVendorType: str = Field(default="GPU_PROVIDER_NVIDIA", description="GPU vendor type")
    numGPU: int = Field(..., description="Number of GPUs")


class SupportedOSTypes(BaseModel):
    architecture: str = Field(default="x86_64", description="OS architecture")
    distribution: str = Field(default="RHEL", description="OS distribution")
    license: str = Field(default="OS_LICENSE_TYPE_FREE", description="OS license type")
    version: str = Field(default="OS_VERSION_UBUNTU_2204_LTS", description="OS version")


class FlavourSupported(BaseModel):
    cpuArchType: str = Field(default="ISA_X86", description="CPU architecture type")
    cpuExclusivity: bool = Field(default=True, description="CPU exclusivity")
    fpga: int = Field(default=0, description="Number of FPGAs")
    gpu: Optional[List[GPU]] = Field(default=None, description="List of GPUs")
    hugepages: List[Hugepages] = Field(
        default_factory=lambda: [Hugepages()], description="List of hugepages"
    )
    memorySize: int = Field(..., description="Memory size in MB")
    numCPU: int = Field(..., description="Number of CPUs")
    storageSize: int = Field(default=0, description="Storage size in GB")
    supportedOSTypes: List[SupportedOSTypes] = Field(
        default_factory=lambda: [SupportedOSTypes()],
        description="List of supported OS types",
    )
    vpu: int = Field(default=0, description="Number of VPUs")


class Flavour(BaseModel):
    id: Optional[str] = None
    date: Optional[int] = None
    zone_id: Optional[str] = None
    flavour_supported: FlavourSupported


# Artefact


class RepoType(str, Enum):
    UPLOAD = "UPLOAD"
    PUBLICREPO = "PUBLICREPO"
    PRIVATEREPO = "PRIVATEREPO"


class ArtefactOnboarding(BaseModel):
    artefact_id: str
    name: str
    # chart: Optional[bytes] = Field(default=None) # XXX AFAIK not supported by CAMARA.
    repo_password: Optional[str] = None
    repo_name: Optional[str] = None
    repo_type: RepoType
    repo_url: Optional[str] = None
    repo_token: Optional[str] = None
    repo_user_name: Optional[str] = None
    model_config = ConfigDict(use_enum_values=True)


# Application Onboarding


class AppComponentSpec(BaseModel):
    artefactId: str
    componentName: Optional[str] = None
    serviceNameEW: Optional[str] = None
    serviceNameNB: Optional[str] = None


class AppMetaData(BaseModel):
    appDescription: Optional[str] = None
    appName: str = Field(default="Default App")
    category: str = Field(default="DEFAULT")
    mobilitySupport: bool = Field(default=False)
    version: str = Field(default="1.0")
    accessToken: Optional[str] = None


class AppQoSProfile(BaseModel):
    appProvisioning: bool = Field(default=True)
    bandwidthRequired: int = Field(default=1)
    latencyConstraints: str = Field(default="NONE")
    mobilitySupport: Optional[bool] = None
    multiUserClients: str = Field(default="APP_TYPE_SINGLE_USER")
    noOfUsersPerAppInst: int = Field(default=1)


class ApplicationOnboardingData(BaseModel):
    appComponentSpecs: List[AppComponentSpec]
    appDeploymentZones: Optional[List[str]] = None
    app_id: str
    appMetaData: AppMetaData = Field(default_factory=AppMetaData)
    appProviderId: str = Field(default="default_provider")
    appQoSProfile: Optional[AppQoSProfile] = None
    appStatusCallbackLink: Optional[str] = None


class ApplicationOnboardingRequest(BaseModel):
    profile_data: ApplicationOnboardingData


# Application Deployment


class AppParameters(BaseModel):
    namespace: Optional[str] = None


class AppDeployData(BaseModel):
    appId: str
    appProviderId: str
    appVersion: str
    zoneInfo: ZoneInfoRef


class AppDeploy(BaseModel):
    app_deploy_data: AppDeployData
    app_parameters: Optional[AppParameters] = Field(default=AppParameters())


class AppDeployResponse(BaseModel):
    Message: str
    app_instance_id: str
    deploy_status: str
    zoneID: str


class AppMigration(BaseModel):
    node_to_deploy: str
    zone_id_to_deploy: str
