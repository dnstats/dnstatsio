import enum

from dnstats.dnsvalidate.util import MaxValue, validate_numbers, is_an_ip
from dnstats.dnsutils import validate_domain

import publicsuffix2


class MXErrors(enum.Enum):
    NO_MX_RECORDS = 0
    BLANK_MX_RECORD = 1
    TOO_MANY_PARTS = 2
    TOO_FEW_PARTS = 3
    PREFERENCE_OUT_OF_RANGE = 4
    INVALID_PREFERENCE = 5
    INVALID_EXCHANGE = 6
    EXCHANGE_IS_AN_IP = 7
    NOT_PUBLIC_DOMAIN = 8
    POSSIBLE_BAD_EXCHANGE = 9


class MxRecord:
    def __init__(self, preference: int, exchange: str):
        self.preference = preference
        self.exchange = exchange


class Mx:
    def __init__(self, mx_records: list):
        self.mx_records = mx_records
        self._validate()

    def _validate(self) -> dict:
        result = dict()
        result['errors'] = []
        result['records'] = []
        if not self.mx_records or len(self.mx_records) == 0:
            result['errors'].append(MXErrors.NO_MX_RECORDS)
            self.errors = result['errors']
            return result

        for record in self.mx_records:
            if not record:
                result['errors'].append(MXErrors.BLANK_MX_RECORD)
                continue
            parts = record.split(' ')

            if len(parts) > 2:
                result['errors'].append(MXErrors.TOO_MANY_PARTS)
                continue

            if len(parts) < 2:
                result['errors'].append(MXErrors.TOO_FEW_PARTS)
                continue

            preference = parts[0]
            exchange = parts[1]

            # Check preference to be an unsigned 16 bit int, RFC 974 (Page 2)
            preference, preference_errors = validate_numbers(preference, MXErrors.INVALID_PREFERENCE,
                                                                  MXErrors.PREFERENCE_OUT_OF_RANGE, MaxValue.USIXTEEN)
            result['errors'].extend(preference_errors)

            if preference_errors:
                continue

            if is_an_ip(exchange):
                result['errors'].append(MXErrors.EXCHANGE_IS_AN_IP)
                continue

            if not validate_domain(exchange):
                result['errors'].append(MXErrors.INVALID_EXCHANGE)
                continue

            if not publicsuffix2.get_tld(exchange) in publicsuffix2.PublicSuffixList().tlds:
                result['errors'].append(MXErrors.NOT_PUBLIC_DOMAIN)
                continue

            if not exchange.endswith('.') and exchange.endswith(publicsuffix2.get_tld(exchange)):
                result['errors'].append(MXErrors.POSSIBLE_BAD_EXCHANGE)

            result['records'].append(MxRecord(preference, exchange))

        self.errors = result['errors']
        self.valid_mx_records = result['records']
        return result
