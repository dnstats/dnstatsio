import enum


class SoaErrors(enum.Enum):
    NO_SOA = 0
    TOO_MANY_SOA = 1
    SOA_INVALID = 2


class Soa:
    """
    Start of Authority record (SOA record) checker
    """
    def __init__(self, soas: list, domain: str):
        self.soas = soas
        self.domain = domain

    def validate(self) -> [int, []]:
        errors = []
        if len(self.soas) == 0:
            errors.append(SoaErrors.NO_SOA)
            return 0, errors

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
        exprire = soa_parts[5]
        minimum = soa_parts[6]


