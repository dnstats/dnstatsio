from enum import Enum

import ipaddress

from dnstats.dnsutils import safe_query


class NsErrors(Enum):
    NO_NS_RECORDS = 0
    ONLY_ONE_NS_RECORD = 1
    NULL_NS_RECORD = 2
    NAMESERVER_HAS_NO_A = 3
    NAMESERVER_HAS_INVALID_RESPONSE = 4
    NAMESERVER_IS_NOT_PUBLIC = 5


class Ns:
    """
    Validate NS records for a given domain.
    """
    def __int__(self, ns_records: list, domain: str):
        """
        Setup an name server check

        :param ns_records: List of NS record for the given domain
        :param domain: Domain of the check, needs to match the given ns records
        """
        self.domain = domain
        self.ns_records = ns_records
        self._result = self.validate()
        self.errors = self._result['errors']
        self.validated_nameservers = self._result['validated_nameservers']

    def _validate(self) -> {}:
        result = {}
        errors = []
        if not self.ns_records or len(self.ns_records) == 0:
            errors.append(NsErrors.NO_NS_RECORDS)
            result['errors'] = errors
            return result

        if len(self.ns_records) == 1:
            errors.append(NsErrors.ONLY_ONE_NS_RECORD)

        validated_records = []
        for ns_record in self.ns_records:
            if not ns_record:
                errors.append(NsErrors.NULL_NS_RECORD)
                break
            ns_lookup_results = safe_query(ns_record, 'a')
            ns_lookup_results += safe_query(ns_record, 'aaaa')
            if not ns_lookup_results:
                errors.append(NsErrors.NAMESERVER_HAS_NO_A)

            for ns_lookup_result in ns_lookup_results:
                try:
                    r = ipaddress.ip_address(ns_lookup_result)
                    if not r.is_global:
                        errors.append(NsErrors.NAMESERVER_IS_NOT_PUBLIC)
                        break
                except:
                    errors.append(NsErrors.NAMESERVER_HAS_INVALID_RESPONSE)
                    break

                validated_records.append(ns_record)

        result['errors'] = errors
        result['validated_nameservers'] = validated_records
        return result
