from dnstats.dnsvalidate.caa import Caa, CAAErrors


def grade(caa_records: list, domain: str) -> [int, ()]:
    if len(caa_records) == 0:
        return 0, [CAAErrors.NO_CAA_RECORDS]
    caa = Caa(caa_records, domain)
    current_grade = 0
    if len(caa.issue) != 0:
        current_grade += 85
    if len(caa.issuewild) != 0:
        current_grade += 10
    if len(caa.iodef) != 0:
        current_grade += 5

    current_grade -= len(caa.errors) * 2

    return current_grade, caa.errors
