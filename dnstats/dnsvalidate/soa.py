import enum


from dnstats.dnsutils import validate_domain
from dnsvalidate.util import validate_numbers, MaxValue


class SoaErrors(enum.Enum):
    NO_SOA = 0
    TOO_MANY_SOA = 1
    SOA_INVALID = 2
    INVALID_MNAME = 3
    INVALID_RNAME = 4
    INVALID_SERIAL = 5
    INVALID_REFRESH = 6
    INVALID_RETRY = 7
    INVALID_EXPIRE = 8
    INVALID_MINIMUM = 9
    SERIAL_NOT_IN_RANGE = 10
    REFRESH_NOT_IN_RANGE = 11
    RETRY_NOT_IN_RANGE = 12
    MINIMUM_NOT_IN_RANGE = 13
    EXPIRE_NOT_IN_RANGE = 14


class Soa:
    """
    Start of Authority record (SOA record) checker.

    Based on the following sources
    - RFC 1035 (https://tools.ietf.org/html/rfc1035)
    """
    def __init__(self, soas: list, domain: str):
        """
        Create an Soa object to check an domain SOA record
        :param soas: the results of from query on soa
        :param domain:
        """
        self.soas = soas
        self.domain = domain
        result = self.validate()
        self.errors = result.get('errors')
        self.mname = result.get('mname')
        self.rname = result.get('rname')
        self.refresh = result.get('refresh')
        self.retry = result.get('retry')
        self.expire = result.get('expire')
        self.minimum = result.get('minimum')
        self.serial = result.get('serial')

    def validate(self) -> {}:
        result = {}
        errors = []
        if len(self.soas) == 0:
            errors.append(SoaErrors.NO_SOA)
            result['errors'] = errors
            return result

        if len(self.soas) != 1:
            errors.append(SoaErrors.TOO_MANY_SOA)
            errors.append(errors)
            result['errors'] = errors
            return result

        soa = self.soas[0]
        soa_parts = soa.split(' ')
        if len(soa_parts) != 7:
            errors.append(SoaErrors.SOA_INVALID)
            result['errors'] = errors
            return result

        mname = soa_parts[0]
        rname = soa_parts[1]
        serial = soa_parts[2]
        refresh = soa_parts[3]
        retry = soa_parts[4]
        expire = soa_parts[5]
        minimum = soa_parts[6]
        if not validate_domain(mname):
            errors.append(SoaErrors.INVALID_MNAME)
        result['mname'] = mname

        if not validate_domain(rname):
            errors.append(SoaErrors.INVALID_RNAME)
        result['rname'] = rname

        result['serial'], serial_errors = validate_numbers(serial, SoaErrors.INVALID_SERIAL,
                                                           SoaErrors.SERIAL_NOT_IN_RANGE, MaxValue.UTHIRTY_TW0)
        errors.extend(serial_errors)

        result['refresh'], refresh_errors = validate_numbers(refresh, SoaErrors.INVALID_REFRESH,
                                                             SoaErrors.REFRESH_NOT_IN_RANGE, MaxValue.UTHIRTY_TW0)
        errors.extend(refresh_errors)

        result['retry'], retry_errors = validate_numbers(retry, SoaErrors.INVALID_RETRY,
                                                         SoaErrors.RETRY_NOT_IN_RANGE, MaxValue.UTHIRTY_TW0)
        errors.extend(retry_errors)

        result['expire'], expire_errors = validate_numbers(expire, SoaErrors.INVALID_EXPIRE,
                                                           SoaErrors.EXPIRE_NOT_IN_RANGE, MaxValue.UTHIRTY_TW0)
        errors.extend(expire_errors)

        result['minimum'], minimum_errors = validate_numbers(minimum, SoaErrors.INVALID_MINIMUM,
                                                             SoaErrors.MINIMUM_NOT_IN_RANGE, MaxValue.UTHIRTY_TW0)
        errors.extend(minimum_errors)

        result['errors'] = errors
        return result
