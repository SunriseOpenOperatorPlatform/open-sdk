#!/usr/bin/env python3
# -*- coding: utf-8 -*-
##
# This file is part of the Open SDK
#
# Contributors:
#   - Sergio Giménez (sergio.gimenez@i2cat.net)
#   - César Cajas (cesar.cajas@i2cat.net)
##
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ZoneInfo(BaseModel):
    flavourId: str
    zoneId: str


class AppParameters(BaseModel):
    namespace: Optional[str] = None


class AppDeployData(BaseModel):
    appId: str
    appProviderId: str
    appVersion: str
    zoneInfo: ZoneInfo


class AppDeploy(BaseModel):
    app_deploy_data: AppDeployData
    app_parameters: Optional[AppParameters] = Field(default=AppParameters())


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

# XXX Leaving default values since i2edge only cares about appid and artifactid, at least for now.


class AppComponentSpec(BaseModel):
    artefactId: str
    componentName: str = Field(default="default_component")
    serviceNameEW: str = Field(default="default_ew_service")
    serviceNameNB: str = Field(default="default_nb_service")


class AppMetaData(BaseModel):
    appDescription: str = Field(default="Default app description")
    appName: str = Field(default="Default App")
    category: str = Field(default="DEFAULT")
    mobilitySupport: bool = Field(default=False)
    version: str = Field(default="1.0")


class AppQoSProfile(BaseModel):
    appProvisioning: bool = Field(default=True)
    bandwidthRequired: int = Field(default=1)
    latencyConstraints: str = Field(default="NONE")
    multiUserClients: str = Field(default="APP_TYPE_SINGLE_USER")
    noOfUsersPerAppInst: int = Field(default=1)


class ApplicationOnboardingData(BaseModel):
    appComponentSpecs: List[AppComponentSpec]
    appDeploymentZones: List[str] = Field(default=["default_zone"])
    app_id: str
    appMetaData: AppMetaData = Field(default_factory=AppMetaData)
    appProviderId: str = Field(default="default_provider")
    appQoSProfile: AppQoSProfile = Field(default_factory=AppQoSProfile)
    appStatusCallbackLink: Optional[str] = None


class ApplicationOnboardingRequest(BaseModel):
    profile_data: ApplicationOnboardingData


# Flavour


class GPU(BaseModel):
    gpuMemory: int = Field(default=0, description="GPU memory in MB")
    gpuModeName: str = Field(default="", description="GPU mode name")
    gpuVendorType: str = Field(
        default="GPU_PROVIDER_NVIDIA", description="GPU vendor type"
    )
    numGPU: int = Field(..., description="Number of GPUs")


class Hugepages(BaseModel):
    number: int = Field(default=0, description="Number of hugepages")
    pageSize: str = Field(default="2MB", description="Size of hugepages")


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
    memorySize: str = Field(..., description="Memory size (e.g., '1024MB' or '2GB')")
    numCPU: int = Field(..., description="Number of CPUs")
    storageSize: int = Field(default=0, description="Storage size in GB")
    supportedOSTypes: List[SupportedOSTypes] = Field(
        default_factory=lambda: [SupportedOSTypes()],
        description="List of supported OS types",
    )
    vpu: int = Field(default=0, description="Number of VPUs")

    @field_validator("memorySize")
    @classmethod
    def validate_memory_size(cls, v):
        if not (v.endswith("MB") or v.endswith("GB")):
            raise ValueError("memorySize must end with MB or GB")
        try:
            int(v[:-2])
        except ValueError:
            raise ValueError("memorySize must be a number followed by MB or GB")
        return v


class Flavour(BaseModel):
    flavour_supported: FlavourSupported


# EdgeCloud Zones


class Zone(BaseModel):
    geographyDetails: str
    geolocation: str
    zoneId: str
