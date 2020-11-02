from dnstats.dnsutils import safe_query, query_name_server


def get_name_server_ips(name_servers: []) -> {}:
    result = {}
    for name_server in name_servers:
        ns_results = safe_query(name_server, 'a')
        ns_results += safe_query(name_server, 'aaaa')
        result[name_server] = ns_results

    return result


def get_name_server_results(name_servers: [], domain: str) -> {}:
    result = {}
    for name_server in name_servers:
        ns_results = query_name_server(name_server, domain, 'ns')
        result['name_server'] = ns_results

    return result
