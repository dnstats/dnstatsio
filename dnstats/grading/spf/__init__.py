from enum import Enum

from dnstats.grading import Grade, half_reduce
from dnstats.dnsutils.spf import get_spf_stats, spf
from dnstats.dnsutils import safe_query
from dnstats.dnsvalidate.spf import validate

def grade(spfs: list, domain: str):
    validate(spfs, domain)

def grade_include(errors, parts_to_consider, sub_parts):
    include_result = safe_query(sub_parts[1], 'txt')
    has_spf = False
    for record in include_result:
        record = record.replace('"', '')
        if record.startswith('v=spf1'):
            if has_spf is False:
                for spf_part in record.split(' '):
                    parts_to_consider.append(spf_part)
            else:
                errors.append(SpfError.INCLUDE_RETURNED_MANY_SPF)
            has_spf = True


def grade_final_qualifer(current_grade, errors, final):
    # TODO: account for only redirect records
    if final == '-all':
        current_grade = Grade.A
    elif final == '~all':
        current_grade = Grade.B
    elif final == '?all':
        current_grade = Grade.C
    elif final == '+all':
        current_grade = Grade.D
    else:
        errors.append(SpfError.DEFAULT_ALL_QUALIFIER)
        current_grade = Grade.C_MINUS
    return current_grade
