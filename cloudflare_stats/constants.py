""" constants """


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
