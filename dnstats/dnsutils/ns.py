from dnstats.dnsutils import safe_query, query_name_server


def get_name_server_ips(name_servers: []) -> {}:
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
    result = {}
    for name_server in list(name_servers.keys()):
        ns_results = query_name_server(name_servers[name_server], domain, 'ns')
        result[name_server] = ns_results
    return result
