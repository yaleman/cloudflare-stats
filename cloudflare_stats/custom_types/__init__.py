""" blep """
from datetime import datetime

from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

VALID_TIME_TYPES = ("hours", "days",)

class ConfigFile(BaseModel):
    """ config file def """
    cloudflare_auth_email: str
    cloudflare_auth_token: str
    splunk_hostname: str
    splunk_token: str
    splunk_hec_port: Optional[int] = 8088
    splunk_index: str = "cloudflare"
    time_type: Optional[str] = Field(None)

    @field_validator("time_type")
    def validate_time_type(cls, value: str) -> str:
        """validates that time_type is a valid value, should be one of hours, days"""
        if value not in VALID_TIME_TYPES:
            raise ValueError(f"Value needs to be one of {','.join(VALID_TIME_TYPES)}")
        return value

class CloudflareZoneMeta(BaseModel):
    """ meta field for CloudflareZone """
    step: Optional[int]
    custom_certificate_quota: Optional[int] = Field(None)
    page_rule_quota: Optional[int] = Field(None)
    phishing_detected: Optional[bool] = Field(None)
    multiple_railguns_allowed: Optional[bool] = Field(None)
class CloudflareZoneOwner(BaseModel):
    """ meta field for CloudflareZone """
    id: Optional[str] = None
    type: str
    email: Optional[str] = None

class CloudflareZoneAccount(BaseModel):
    """ meta field for CloudflareZone """
    id: str
    name: str

class CloudflareZonePlan(BaseModel):
    """ meta field for CloudflareZone """
    id: str
    name: str
    price: float
    currency: str
    frequency: Optional[str] = Field(None)
    is_subscribed: Optional[bool] = Field(None)
    can_subscribe: Optional[bool] = Field(None)
    legacy_id: str
    legacy_discount: Optional[bool] = Field(None)
    externally_managed: Optional[bool] = Field(None)

class CloudflareZone(BaseModel):
    """ cloudflare zone """
    id: str
    status: str
    paused: Optional[bool]
    type: str
    development_mode: Optional[int]
    name_servers: List[str]
    original_name_servers: Optional[List[str]]  = Field(None)
    original_registrar: Optional[str]  = Field(None)
    original_dnshost: Optional[str]  = Field(None)
    modified_on: datetime
    created_on: datetime
    activated_on: datetime
    meta: CloudflareZoneMeta
    owner: CloudflareZoneOwner
    account: CloudflareZoneAccount
    plan: CloudflareZonePlan
    domain: str = Field(..., alias="name")
    permissions: Optional[List[str]]  = Field(None)
