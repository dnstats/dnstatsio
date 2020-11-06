import enum

from dnstats.dnsutils import validate_domain


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
    INVALID_TTL = 9
    SERIAL_NOT_IN_RANGE = 10


class Soa:
    """
    Start of Authority record (SOA record) checker.

    Based on the following sources
    - RFC 1035 (https://tools.ietf.org/html/rfc1035)
    """
    def __init__(self, soas: list, domain: str):
        self.soas = soas
        self.domain = domain
        self.errors = self.validate['errors']


    def validate(self) -> {}:
        result = {}
        errors = []
        if len(self.soas) == 0:
            errors.append(SoaErrors.NO_SOA)
            return result

        if len(self.soas) != 1:
            errors.append(SoaErrors.TOO_MANY_SOA)

        soa = self.soas[0]
        soa_parts = soa.split(' ')
        if len(soa_parts) != 7:
            errors.append(SoaErrors.SOA_INVALID)

        mname = soa_parts[0]
        rname = soa_parts[1]
        serial = soa_parts[2]
        refresh = soa_parts[3]
        retry = soa_parts[4]
        expire = soa_parts[5]
        minimum = soa_parts[6]
        if not validate_domain(mname):
            errors.append(SoaErrors.INVALID_MNAME)

        if not validate_domain(rname):
            errors.append(SoaErrors.INVALID_RNAME)



        if serial > 4294967295 or serial < 0:
            errors.append(SoaErrors.SERIAL_NOT_IN_RANGE)


        result['errors'] = errors
        return result
