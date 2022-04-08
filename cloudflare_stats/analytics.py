""" analytics thing """

# TODO: can we pydantic errors when it finds extra fields?
from datetime import datetime, timedelta
import json
import logging
import sys
from typing import Any, Dict, Generator, List, Optional, Union

import click
from loguru import logger
import requests
from splunk_http_event_collector import http_event_collector #type:ignore

from . import k2v, setup_logging, auth_headers, load_config
from .constants import DAYS_HENCE, DATE_FORMAT, DATETINE_FORMAT, HOURS_HENCE, QUERY_STRING
from .custom_types import ConfigFile, CloudflareZone
from .custom_types.analytics import AnalyticsDayData


# pylint: disable=too-many-arguments
def get_analytics(
    zone_id: str,
    config_file: ConfigFile,
    earliest: Optional[str] = None,
    latest: Optional[str] = None,
    query_type: str="days",
    time_count: Optional[int] = None
    ) -> List[Dict[str, Any]]:
    """ analytics query """

    if query_type == "days":
        if time_count is None:
            time_count=DAYS_HENCE
        if earliest is None:
            earliest_date = datetime.utcnow() - timedelta(days=int(time_count))
            earliest = earliest_date.strftime(DATE_FORMAT)
        if latest is None:
            latest=datetime.utcnow().strftime(DATE_FORMAT)
        querystring = str(QUERY_STRING)
    elif query_type == "hours":
        if time_count is None:
            time_count=HOURS_HENCE
        if earliest is None:
            earliest_date = datetime.utcnow() - timedelta(hours=int(time_count))
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

@click.command()
@click.option("--debug", "-d", is_flag=True, default=False)
@click.option(
    "--time-type", "-t",
    help="Either 'days' or 'hours', defaults to 'days'",
    )
@click.option("--time-count", "-c", help="number of intervals (days/hours) to go back")
def cli(
    time_count: Optional[int]=None,
    time_type: Optional[str]=None,
    debug: bool=False,
    ) -> None:
    """ Analytics downloader for Cloudflare data """
    setup_logging(debug)
    config = load_config()

    logger.debug(config.dict())

    if time_type is None:
        if config.time_type is not None:
            time_type = config.time_type
        else:
            time_type = "days"


    if time_type not in ["days", "hours",]:
        logger.error("time-type setting needs to be either days or hours, got '{}'", time_type)
        sys.exit(1)

    logger.debug("Starting HEC")
    hec = http_event_collector(
        token=config.splunk_token,
        http_event_server=config.splunk_hostname,
        http_event_port=config.splunk_hec_port,
        http_event_server_ssl=True,
        )
    hec.input_type = "json"
    hec.index = config.splunk_index
    hec.log.setLevel(logging.DEBUG)

    logger.debug("Pulling list of zones...")
    for zone_info in get_zones(config):
        del zone_info["permissions"]
        logger.debug("Parsing zone")
        zone = CloudflareZone.parse_obj(zone_info)

        logger.info(zone.domain)

        payload={
            "sourcetype" : "cloudflare:zone",
            "event" : zone.dict()
        }
        hec.batchEvent(payload)

        zone_analytics = get_analytics(
                    zone_id=zone.id,
                    config_file=config,
                    query_type=time_type,
                    time_count=time_count,
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

            if time_type == "days":
                data_raw["timeslot"] = f"{data_raw['dimensions']['timeslot']}T00:00:00Z"
            else:
                data_raw["timeslot"] = data_raw["dimensions"]["timeslot"]
            eventtime = datetime.strptime(
                data_raw["timeslot"],
                "%Y-%m-%dT%H:%M:%S%z"
            )

            # clean out re-mapped fields
            del data_raw["dimensions"]
            del data_raw["sum"]

            timeslot_data = AnalyticsDayData.parse_obj(data_raw)
            logger.debug(
                "Successfully parsed {} {}",
                zone.domain,
                timeslot_data.dict()["timeslot"],
                )
            timeslot_data.zone_id = zone.id
            timeslot_data.domain = zone.domain
            payload = {
                "sourcetype" : "cloudflare:analytics",
                "event" : timeslot_data.dict(exclude_none=True, exclude_unset=True),
            }
            logger.debug(json.dumps(payload, indent=4, default=str))

            hec.batchEvent(
                payload,
                eventtime=eventtime.timestamp(),
                )
            hec.flushBatch()

    hec.flushBatch()

if __name__ == "__main__":
    cli()
