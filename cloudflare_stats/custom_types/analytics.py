""" analytics types """

from typing import Dict, Optional

from pydantic import BaseModel, Field

FIELD_TYPENAME = Field(..., alias="__typename")

# class AnalyticsDayDataDimensions(BaseModel):
#     """ dimensions field """
#     # typename: str = FIELD_TYPENAME
#     timeslot: str


class AnalyticsDayDataUnique(BaseModel):
    """sum data"""

    # typename: str = FIELD_TYPENAME
    uniques: int


class AnalyticsBrowserMap(BaseModel):
    """browserMap field"""

    # typename: str = FIELD_TYPENAME
    # user_agent: str = Field(..., alias="key")
    page_views: int = Field(..., alias="pageViews")


class AnalyticsClientSSLMap(BaseModel):
    """clientSSLMap field"""

    # typename: str = FIELD_TYPENAME
    # ssl_type: str = Field(..., alias="key")
    requests: int


class AnalyticsContentTypeMap(BaseModel):
    """contentTypeMap field"""

    # typename: str = FIELD_TYPENAME
    # file_type: str = Field(..., alias="key")
    requests: int


class AnalyticsCountryMap(BaseModel):
    """countryMap field"""

    # typename: str = FIELD_TYPENAME
    # country_code: Optional[str] = Field(..., alias="key")
    requests: int
    threats: int


class AnalyticsIPClassMap(BaseModel):
    """countryMap field"""

    # typename: str = FIELD_TYPENAME
    # ip_type: str = Field(..., alias="key")
    requests: int


class AnalyticsResponseStatusMap(BaseModel):
    """responseStatusMap field"""

    # typename: str = FIELD_TYPENAME
    # status_code: int = Field(..., alias="key")
    requests: int


class AnalyticsThreatPathingMap(BaseModel):
    """threatPathingMap field"""

    # typename: str = FIELD_TYPENAME
    # threat_pathing: str = Field(..., alias="key")
    requests: int


# class AnalyticsDayDataSum(BaseModel):
#     """ sum data """


class AnalyticsDayData(BaseModel):
    """single day's response from the graphql API"""

    # typename: str = FIELD_TYPENAME
    # dimensions: AnalyticsDayDataDimensions
    # sum: AnalyticsDayDataSum
    uniq: AnalyticsDayDataUnique
    zone_id: Optional[str] = None
    domain: Optional[str] = None

    # typename: str = FIELD_TYPENAME
    browser_map: Dict[str, AnalyticsBrowserMap] = Field(..., alias="browserMap")
    bytes: int
    cached_bytes: int = Field(..., alias="cachedBytes")
    cached_requests: int = Field(..., alias="cachedRequests")
    client_ssl_map: Dict[str, AnalyticsClientSSLMap] = Field(..., alias="clientSSLMap")
    content_type_map: Dict[str, AnalyticsContentTypeMap] = Field(
        ..., alias="contentTypeMap"
    )
    country_map: Dict[str, AnalyticsCountryMap] = Field(..., alias="countryMap")
    ip_class_map: Dict[str, AnalyticsIPClassMap] = Field(..., alias="ipClassMap")
    encrypted_bytes: int = Field(..., alias="encryptedBytes")
    encrypted_requests: int = Field(..., alias="encryptedRequests")
    page_views: int = Field(..., alias="pageViews")
    requests: int
    response_status_map: Dict[int, AnalyticsResponseStatusMap] = Field(
        ..., alias="responseStatusMap"
    )
    threat_pathing_map: Dict[str, AnalyticsThreatPathingMap] = Field(
        ..., alias="threatPathingMap"
    )

    timeslot: str
    threats: int
