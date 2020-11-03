from dnstats.dnsutils import safe_query, query_name_server


def get_name_server_ips(name_servers: []) -> {}:
    """
    Get the ips of the given domain names

    :param name_servers:
    :return: dictl keys are the items in the passed list, the values are the IPs (4 and 6) of the key
    """
    result = {}
    if not name_servers:
        return result
    for name_server in name_servers:
        ns_results = []
        a_results = safe_query(name_server, 'a')
        if a_results:
            ns_results += a_results
        aaaa_results = safe_query(name_server, 'aaaa')
        if aaaa_results:
            ns_results += aaaa_results
        result[name_server] = ns_results

    return result


def get_name_server_results(name_servers: {}, domain: str) -> {}:
    """
    Given a set of name servers, get the ns records for the given domain. This method will be used to verity that
    all ns servers give same NS RRSet.
    :param name_servers: list of name servers to check
    :param domain: domain to check
    :return: dict keys are the name servers, values is RRSet as list from that name server
    """
    result = {}
    for name_server in list(name_servers.keys()):
        ns_results = query_name_server(name_servers[name_server], domain, 'ns')
        result[name_server] = ns_results
    return result
