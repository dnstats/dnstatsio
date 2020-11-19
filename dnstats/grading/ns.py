from dnstats.dnsvalidate.ns import Ns, NsErrors
from dnstats.utils import count_value


def grade(ns_records: list, ns_ip_addresses: dict, ns_record_results: dict, domain: str) -> [int, []]:
    ns = Ns(ns_records, ns_ip_addresses, ns_record_results, domain)
    if ns.errors.__contains__(NsErrors.NO_NS_RECORDS):
        return 0, ns.errors

    final_grade = 100
    if ns.errors.__contains__(NsErrors.ONLY_ONE_NS_RECORD):
        final_grade -= 20
    final_grade -= count_value(NsErrors.NO_NS_RECORDS, ns.errors) * 15
    final_grade -= count_value(NsErrors.NULL_NS_RECORD, ns.errors) * 15
    final_grade -= count_value(NsErrors.NAMESERVER_HAS_NO_A, ns.errors) * 15
    final_grade -= count_value(NsErrors.NAMESERVER_HAS_INVALID_RESPONSE, ns.errors) * 15
    final_grade -= count_value(NsErrors.NAMESERVER_IS_NOT_PUBLIC, ns.errors) * 10
    final_grade -= count_value(NsErrors.NO_NAME_SERVERS_RETURNED, ns.errors) * 25
    final_grade -= count_value(NsErrors.NAME_SERVER_MISMATCH, ns.errors) * 10
    return max(0, final_grade), ns.errors
