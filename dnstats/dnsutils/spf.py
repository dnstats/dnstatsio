import re

from dnstats.dnsutils import safe_query

from enum import Enum


class SPFErrors(Enum):
    NO_MX_RECORDS = 0
    TOO_MANY_LOOKUPS = 1
    TOO_MANY_MX_RECORDS_RETURNED = 2


def get_spf_stats(ans):
    """

    :param ans:
    :return:
    """
    if ans:
        for r in ans:
            if 'redirect=' in r:
                r = _get_redirect_record(r)

            if r.startswith('"v=spf'):
                return {'spf_exists': True, 'spf_record': r, 'spf_policy': _spf_final_qualifier(r)}
    return {'spf_exists': False, 'spf_record': None, 'spf_policy': 'no_policy'}


def spf_final_qualifier(record: str) -> str:
    m = re.search(r"[+?~-]all", record)

    if m:
        return m[0]
    else:
        return 'no_policy'


def _get_redirect_record(record):
    record = record.replace('"', '')
    parts = record.split(' ')
    for part in parts:
        if part.startswith('redirect='):
            sub = part.split('=')
            if len(sub) == 2:
                ans = safe_query(sub[1], 'txt')
                if ans:
                    for r in ans:
                        if r.startswith('"v=spf'):
                            return r
    return ''


def get_dns_count(record: str) -> [int, bool, list[SPFErrors]]:
    parts = record.split(' ')
    parts_to_look_at = parts
    count = 0
    valid = True
    errors = list()
    for part in parts_to_look_at:
        if count > 20:
            valid = False
            errors.append(SPFErrors.TOO_MANY_LOOKUPS)
            break
        if part.startswith('include:'):
            count += 1
            include = part.split(':')
            records = safe_query(include[1], 'txt')
            include_parts = None
            for record in records:
                if record.startswith('v=spf1'):
                    include_parts = record.split()
                parts_to_look_at.append(include_parts)
        if part.startswith('a:'):
            count += 1
        if part.startswith('mx'):
            count += 1
            mx_parts = part.split(':')
            ans = safe_query(mx_parts[1], 'mx')
            if len(ans) > 10:
                valid = False
                errors.append(SPFErrors.TOO_MANY_MX_RECORDS_RETURNED)
        if part.startswith('exists:'):
            count += 1

        parts_to_look_at.remove(part)

    return count, valid, errors
