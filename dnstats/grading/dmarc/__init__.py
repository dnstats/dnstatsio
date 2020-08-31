from enum import Enum

from dnstats.grading import Grade, half_reduce, update_count_dict, half_raise, get_grade, not_in_penalty
from dnstats.dnsvalidate.dmarc import Dmarc, DmarcErrors

FO = {'1': 4, 'd': 2, 's': 2}
P = {'none': 10, 'quarantine': 30, 'reject': 60}
RUA_RUF = {'none': 10, 'quarantine': 15, 'reject': 15}
SP = {'none': 0, 'quarantine': 10, 'reject': 15}


def grade(dmarcs: list, domain: str) -> int:
    current_grade = 0
    dmarc = Dmarc(dmarcs)
    print(dmarc.errors)
    if dmarc.errors.__contains__(DmarcErrors.INVALID_DMARC_RECORD_START):
        return 0
    if dmarc.adkim == 's':
        current_grade += 5
    if dmarc.aspf == 's':
        current_grade += 5
    current_grade += get_grade(FO, dmarc.fo, 0)
    current_grade += get_grade(P, dmarc.p, 0)
    if dmarc.p not in P:
        return 0
    current_grade += get_grade(RUA_RUF, dmarc.rua, 0)
    current_grade += get_grade(RUA_RUF, dmarc.ruf, 0)
    if not dmarc.sp:
        current_grade += get_grade(SP, dmarc.p, 0)
    else:
        current_grade += get_grade(SP, dmarc.sp, 0)
    print(dmarc.pct)
    if dmarc.pct == 0:
        current_grade -= 2
    elif 70 >= dmarc.pct <= 90:
        current_grade += 1
    elif 90 > dmarc.pct <= 99:
        current_grade += 3
    elif dmarc.pct == 100:
        current_grade += 5

    if dmarc.rua is not None:
        current_grade += 5

    if dmarc.ruf is not None:
        current_grade += 5

    return current_grade
