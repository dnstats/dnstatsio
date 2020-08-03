from enum import Enum

from dnstats.grading import Grade, half_reduce
from dnsutils.spf import get_spf_stats
from dnstats.dnsutils import safe_query


class SpfError(Enum):
    NONE = 0
    INVALID_RECORD_START = 1
    HAS_PTR = 2
    TOO_MANY_DNS_LOOKUPS = 3
    DEFAULT_ALL_QUALIFIER = 4
    INVALID_INCLUDE_FORMAT = 5
    INCLUDE_RETURNED_MANY_SPF = 6
    TOO_MANY_A_RECORDS_RETURNED = 7
    INVALID_A_MECHANISM = 8
    INVALID_MX_MECHANISM = 9
    TOO_MANY_MX_RECORDS_RETURNED = 10
    INVALID_REDIRECT_MECHANISM = 11
    NO_RECORD_AT_REDIRECT = 12
    REDIRECT_RETURNED_MANY_SPF = 13
    INVALID_IPV4_MECHANISM = 14
    INVALID_IPV6_MECHANISM = 15
    INVALID_MECHANISM = 16


def grade(spfs: list, domain: str):
    errors = list()
    current_grade = Grade.F
    if len(spfs) > 1:
        errors.append(SpfError.MULTIPLE_SPF_RECORDS)
        return current_grade, errors
    spf = spfs[0]
    if not spf.startswith('v=spf1 '):
        errors.append(SpfError.INVALID_RECORD_START)
        return current_grade, 
    parts = spf.split(' ')errors
    ptr = parts.__contains__('ptr')
    final = get_spf_stats([spf])[2]
    count = 1
    parts_to_consider = list()
    parts_to_consider.extend(parts)

    current_grade = grade_final_qualifer(current_grade, errors, final)

    inter = 0
    for part in parts_to_consider:
        inter += 1
        if count >= 10:
            current_grade = half_reduce(current_grade)
            errors.append(SpfError.TOO_MANY_DNS_LOOKUPS)
            break

        if part.startswith('include'):
            count += 1
            sub_parts = part.split(':')
            if len(sub_parts) == 2:
                grade_include(errors, parts_to_consider, sub_parts)
            else:
                errors.append(SpfError.INVALID_INCLUDE_FORMAT)
                break
        if part.startswith('a'):
            count += 1
            a_result = safe_query(domain, 'a')
            if len(a_result) > 10:
                errors.append(SpfError.TOO_MANY_A_RECORDS_RETURNED)
                break
        if part.startswith('mx'):
            count += 1
            mx_result = safe_query(domain, 'a')
            if len(mx_result) > 10:
                errors.append(SpfError.TOO_MANY_MX_RECORDS_RETURNED)

        if part.startswith('ptr'):
            # Count as one DNS query. No way to valid this without an email
            count += 1
        if part.startswith('exists'):
            # We don't need to valid the name exists, as not exisitng is a valid part of the flow
            count += 1
        if part.startswith('redirect'):
            sub_parts = part.split('=')
            # TODO: check if valid DNS Name
            if len(sub_parts) == 2:
                redirect_query = safe_query(sub_parts[1], 'txt')
                if redirect_query is None or len(redirect_query):
                    errors.append(SpfError.INVALID_REDIRECT_MECHANISM)
                has_spf = False
                for record in redirect_query:
                    record = record.replace('"', '')
                    if record.startswith('v=spf1 '):
                        if not has_spf:
                            for spf_part in record.split(' '):
                                parts_to_consider.append(spf_part)
                            has_spf = True
                if not has_spf:
                    errors.append(SpfError.NO_RECORD_AT_REDIRECT)
            else:
                errors.append(SpfError.INVALID_REDIRECT_MECHANISM)
            count += 1

            if part.startswith('ipv4'):
                # TODO: validate IP address
                pass

            elif part.startswith('ipv6'):
                # TODO: validate IP address
                pass

            elif part.startswith('exp='):
                pass
            else:
                errors.append(SpfError.INVALID_MECHANISM)
                break

    if ptr:
        current_grade = half_reduce(current_grade)
        errors.append(SpfError.HAS_PTR)

    return current_grade, errors


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
