import re

from dnstats.dnsutils import safe_query


def get_spf_stats(ans):
    if ans:
        for r in ans:
            if 'redirect=' in r:
                r = _get_redirect_record(r)

            if r.startswith('"v=spf'):
                return True, r, _spf_final_qualifier(r)
    return False, None, 'no_policy'


def _spf_final_qualifier(record: str) -> str:
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




