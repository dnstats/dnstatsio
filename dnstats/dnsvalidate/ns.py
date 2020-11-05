from enum import Enum

import ipaddress


class NsErrors(Enum):
    NO_NS_RECORDS = 0
    ONLY_ONE_NS_RECORD = 1
    NULL_NS_RECORD = 2
    NAMESERVER_HAS_NO_A = 3
    NAMESERVER_HAS_INVALID_RESPONSE = 4
    NAMESERVER_IS_NOT_PUBLIC = 5
    NO_NAME_SERVERS_RETURNED = 6
    NAME_SERVER_MISMATCH = 7


class Ns:
    """
    Validate NS records for a given domain.
    """
    def __init__(self, ns_records: list, ns_ip_addresses: dict, ns_server_ns_results: dict,  domain: str):
        """
        Setup an name server check

        :param ns_records: List of NS record for the given domain
        :param ns_ip_addresses:
        :param ns_server_ns_results:
        :param domain: Domain of the check, needs to match the given ns records
        """
        self.domain = domain
        self.ns_records = ns_records
        self.ns_ip_addresses = ns_ip_addresses
        self.ns_server_ns_results = ns_server_ns_results
        self._result = self._validate()
        self.errors = self._result['errors']
        self.validated_nameservers = self._result['validated_nameservers']

    def _validate(self) -> {}:
        result = {}
        errors = []
        validated_records = []
        if not self.ns_records or len(self.ns_records) == 0:
            errors.append(NsErrors.NO_NS_RECORDS)
            result['errors'] = errors
            result['validated_nameservers'] = validated_records
            return result

        if len(self.ns_records) == 1:
            errors.append(NsErrors.ONLY_ONE_NS_RECORD)

        for record in list(self.ns_ip_addresses.keys()):
            if not self.ns_ip_addresses[record]:
                errors.append(NsErrors.NULL_NS_RECORD)
            for ip in self.ns_ip_addresses[record]:
                try:
                    r = ipaddress.ip_address(ip)
                    if not r.is_global:
                        errors.append(NsErrors.NAMESERVER_IS_NOT_PUBLIC)
                        break
                except:
                    errors.append(NsErrors.NAMESERVER_HAS_INVALID_RESPONSE)
                    break
            validated_records.append(record)

        sets = list()
        for ns_server in list(self.ns_server_ns_results.keys()):
            the_set = set()
            for ns_result in self.ns_server_ns_results[ns_server]:
                the_set.add(ns_result)
            sets.append(the_set)

        for outer_set in sets:
            for inner_set in sets:
                if outer_set != inner_set:
                    errors.append(NsErrors.NAME_SERVER_MISMATCH)

        if len(sets) == 0:
            errors.append(NsErrors.NO_NAME_SERVERS_RETURNED)

        result['errors'] = errors
        result['validated_nameservers'] = validated_records
        return result
