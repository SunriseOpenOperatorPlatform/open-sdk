# EXAMPLE OF PYDANTIC SCHEMAS
from typing import Optional

from pydantic import AnyHttpUrl, BaseModel, Field


class _AdapterBase(BaseModel):
    client_name: str = Field(..., min_length=1)
    base_url: AnyHttpUrl

    class Config:
        extra = "allow"


class EdgeCloudConfig(_AdapterBase):
    pass


class NetworkConfig(_AdapterBase):
    pass


class AdapterSpecs(BaseModel):
    edgecloud: Optional[EdgeCloudConfig] = None
    network: Optional[NetworkConfig] = None

    class Config:
        extra = "forbid"
