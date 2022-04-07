""" analytics thing """

# TODO: can we pydantic errors when it finds extra fields?
from datetime import datetime, timedelta
import json
import logging
from pathlib import Path
import sys
from typing import Any, Dict, Generator, List, Optional, Union

import click
from loguru import logger
import requests
from splunk_http_event_collector import http_event_collector #type:ignore

from . import k2v, setup_logging
from .custom_types import ConfigFile, CloudflareZone
from .custom_types.analytics import AnalyticsDayData

DAYS_HENCE = 90
HOURS_HENCE = 36

DATE_FORMAT = "%Y-%m-%d"
DATETINE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

QUERY_STRING = """query GetZoneAnalytics($zoneTag: string, $since: string, $until: string) {
    viewer {
        zones(filter: {zoneTag: $zoneTag}) {
        totals: httpRequests1dGroups(limit: 10000, filter: {date_geq: $since, date_lt: $until}) {
            uniq {
            uniques
            __typename
            }
            __typename
        }
        zones: httpRequests1dGroups(orderBy: [date_ASC], limit: 10000, filter: {date_geq: $since, date_lt: $until}) {
            dimensions {
            timeslot: date
            __typename
            }
            uniq {
            uniques
            __typename
            }
            sum {
            browserMap {
                pageViews
                key: uaBrowserFamily
                __typename
            }
            bytes
            cachedBytes
            cachedRequests
            contentTypeMap {
                bytes
                requests
                key: edgeResponseContentTypeName
                __typename
            }
            clientSSLMap {
                requests
                key: clientSSLProtocol
                __typename
            }
            countryMap {
                bytes
                requests
                threats
                key: clientCountryName
                __typename
            }
            encryptedBytes
            encryptedRequests
            ipClassMap {
                requests
                key: ipType
                __typename
            }
            pageViews
            requests
            responseStatusMap {
                requests
                key: edgeResponseStatus
                __typename
            }
            threats
            threatPathingMap {
                requests
                key: threatPathingName
                __typename
            }
            __typename
            }
            __typename
        }
        __typename
        }
        __typename
    }
    }"""


def auth_headers(config_file: ConfigFile) -> Dict[str,str]:
    """ get the auth headers """
    return {
        "X-AUTH-EMAIL" : config_file.auth_email,
        "Authorization" : f"Bearer {config_file.auth_token}"
    }

def get_analytics(
    zone_id: str,
    config_file: ConfigFile,
    earliest: Optional[str] = None,
    latest: Optional[str] = None,
    query_type: str="days"
    ) -> List[Dict[str, Any]]:
    """ analytics query """




    if query_type == "days":
        if earliest is None:
            earliest_date = datetime.utcnow() - timedelta(days=DAYS_HENCE)
            earliest = earliest_date.strftime(DATE_FORMAT)
        if latest is None:
            latest=datetime.utcnow().strftime(DATE_FORMAT)
        querystring = str(QUERY_STRING)
    elif query_type == "hours":
        if earliest is None:
            earliest_date = datetime.utcnow() - timedelta(hours=HOURS_HENCE)
            earliest = earliest_date.strftime(DATETINE_FORMAT)
        if latest is None:
            latest=datetime.utcnow().strftime(DATETINE_FORMAT)
        querystring = QUERY_STRING.replace("date_", "datetime_")
        querystring = querystring.replace("timeslot: date", "timeslot: datetime")
        querystring = querystring.replace("httpRequests1dGroups", "httpRequests1hGroups")
    # 24 hours
    #'since': '2022-04-06T13:00:00Z',
    #'until': '2022-04-07T13:00:00Z',

    analytics_query = {
        'operationName': 'GetZoneAnalytics',
        'variables': {
            'zoneTag': zone_id,
            'since': earliest,
            'until': latest,
        },
        'query': querystring,
    }

    response = requests.post(
        'https://api.cloudflare.com/client/v4/graphql',
        headers=auth_headers(config_file),
        json=analytics_query,
        )

    try:
        result: List[Dict[str, Any]] = response.json()["data"]["viewer"]["zones"][0]["zones"]
        return result
    except KeyError as key_error:
        logger.error("couldn't get zone data from analytics: {}", key_error)
    except json.JSONDecodeError as json_error:
        logger.error("Failed to decode JSON: {}", json_error)
    sys.exit(1)

def get_zones(
    config_file: ConfigFile,
    per_page: int=50,
    page: Optional[int]=None,
    status: str="active",
    ) -> Generator[Dict[str,Any], None, None]:
    """ get zone information """
    get_zones_url = "https://api.cloudflare.com/client/v4/zones"
    page_value = 1 if page is None else page
    params: Dict[str, Union[str, int]] = {
        "per_page" : per_page,
        "page" : page_value,
        "status": status,
    }
    response = requests.get(
        url=get_zones_url,
        headers=auth_headers(config_file),
        params=params,
    )
    response_data = response.json()
    if "result" not in response_data:
        raise ValueError("result key not in zone data")

    for zone_data in response_data["result"]:
        yield zone_data

    if page is None:
        page = 1

    # check if we need to paginate
    if "result_info" in response_data:
        try:
            total_pages = int(response_data["result_info"]["total_pages"])
        except ValueError:
            return
        if total_pages > page_value:
            for result in get_zones(
                config_file=config_file,
                page = page+1,
                per_page=per_page,
                status=status,
            ):
                yield result


def load_config() -> ConfigFile:
    """ loads config """
    config_filepath = Path("~/.config/cloudflare-stats.json").expanduser().resolve()
    if not config_filepath.exists():
        logger.error("Couldn't find config file, looked in {}", config_filepath)
        sys.exit(1)
    return ConfigFile.parse_file(config_filepath)


@click.command()
@click.option("--debug", "-d", is_flag=True, default=False)
def cli(
    debug: bool=False,
    ) -> None:
    """ Analytics downloader for Cloudflare data """
    config = load_config()

    setup_logging(debug)

    hec = http_event_collector(
        token=config.hec_token,
        http_event_server=config.hec_hostname,
        http_event_port=config.hec_port,
        http_event_server_ssl=True,
        )
    hec.index = config.splunk_index
    hec.log.setLevel(logging.DEBUG)

    for zone_info in get_zones(config):
        del zone_info["permissions"]
        zone = CloudflareZone.parse_obj(zone_info)

        payload={
            "sourcetype" : "cloudflare:zone",
            "event" : zone.dict()
        }
        hec.batchEvent(payload)

        zone_analytics = get_analytics(
                    zone_id=zone.id,
                    config_file=config,
                    query_type="hours",
                    )

        for data_raw in zone_analytics:
            logger.debug("Parsing day: {}", data_raw["dimensions"]["timeslot"])

            for field in data_raw["sum"]:
                data_raw[field] = data_raw["sum"][field]

            data_raw["browserMap"] = k2v(data_raw["browserMap"])
            data_raw["clientSSLMap"] = k2v(data_raw["clientSSLMap"])
            data_raw["contentTypeMap"] = k2v(data_raw["contentTypeMap"])
            data_raw["countryMap"] = k2v(data_raw["countryMap"])
            data_raw["ipClassMap"] = k2v(data_raw["ipClassMap"])
            data_raw["responseStatusMap"] = k2v(data_raw["responseStatusMap"])
            data_raw["threatPathingMap"] = k2v(data_raw["threatPathingMap"])

            data_raw["timeslot"] = data_raw["dimensions"]["timeslot"]

            del data_raw["dimensions"]
            del data_raw["sum"]

            timeslot_data = AnalyticsDayData.parse_obj(data_raw)
            logger.debug("Successfully parsed {} {}", zone.domain, timeslot_data.timeslot)
            timeslot_data.zone_id = zone.id
            timeslot_data.domain = zone.domain
            logger.debug(json.dumps(timeslot_data.dict(), indent=4, default=str))
            payload = {
                "sourcetype" : "cloudflare:analytics",
                "event" : timeslot_data.dict(exclude_none=True, exclude_unset=True),
            }
            hec.batchEvent(payload)
        hec.flushBatch()

    hec.flushBatch()

if __name__ == "__main__":
    cli()
