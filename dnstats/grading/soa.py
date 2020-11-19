from dnstats.dnsvalidate.soa import Soa, SoaErrors


def grade(soas: list, domain: str) -> [int, []]:
    soa = Soa(soas, domain)
    final_grade = 100
    if len(soa.errors) == 0:
        return final_grade, soa.errors
    if soa.errors.__contains__(SoaErrors.NO_SOA):
        return 0, soa.errors

    if soa.errors.__contains__(SoaErrors.SOA_INVALID):
        return 0, soa.errors

    if soa.errors.__contains__(SoaErrors.TOO_MANY_SOA):
        return 0, soa.errors

    return max(final_grade - (5 * len(soa.errors)), 0), soa.errors

