""" constants """

CONFIG_FILE_LOCATIONS =  [
        "cloudflare-stats.json",
        "/etc/cloudflare-stats.json",
        "~/.config/cloudflare-stats.json",
        ]

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
            }
        }
        zones: httpRequests1dGroups(orderBy: [date_ASC], limit: 10000, filter: {date_geq: $since, date_lt: $until}) {
            dimensions {
            timeslot: date
            }
            uniq {
            uniques
            }
            sum {
            browserMap {
                pageViews
                key: uaBrowserFamily
            }
            bytes
            cachedBytes
            cachedRequests
            contentTypeMap {
                bytes
                requests
                key: edgeResponseContentTypeName
            }
            clientSSLMap {
                requests
                key: clientSSLProtocol
            }
            countryMap {
                bytes
                requests
                threats
                key: clientCountryName
            }
            encryptedBytes
            encryptedRequests
            ipClassMap {
                requests
                key: ipType
            }
            pageViews
            requests
            responseStatusMap {
                requests
                key: edgeResponseStatus
            }
            threats
            threatPathingMap {
                requests
                key: threatPathingName
            }
            }
        }
        }
    }
    }"""
