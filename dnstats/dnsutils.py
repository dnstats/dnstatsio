import dns.resolver
import re


def safe_query(site: str, type: str):
    r = None
    try:
        r = dns.resolver.query(site, type)
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
        pass

    if r:
        results = list()
        for ans in r:
            results.append(ans.to_text())
        return results
    else:
        return None


def get_spf_stats(ans):
    for r in ans:
        if r.startswith('"v=spf'):
            return True, r, _spf_final_qualifier(r)
    return False


def _spf_final_qualifier(record: str) -> str:
    m = re.search(r"[+?~-]all", record)
    if m:
        return m[0]
    else:
        return ""


def caa_has_iodef(ans):
    for r in ans:
        if 'iodef' in r:
            return True
    return False


def get_dmarc_stats(ans):
    aggregate = False
    forensic = False
    dmarc = False
    policy = ""
    sub_policy = ""
    for r in ans:
        if r.startswith('"v=DMARC1'):
            dmarc = True
            dmarc_keys = _parse_dmarc(r)

            if 'rua' in dmarc_keys.keys():
                aggregate = True
            if "ruf" in dmarc_keys.keys():
                forensic = True
            if "p" in dmarc_keys.keys():
                policy = dmarc_keys['p']
            if 'sp' in dmarc_keys.keys():
                sub_policy = dmarc_keys['sp']
    return aggregate, forensic, dmarc, policy, sub_policy


def _parse_dmarc(record) -> []:
    record = record.replace('"', '')
    if not record.startswith('v=DMARC1'):
        return []
    parts = record.split(';')
    policy = dict()
    for part in parts:
        subs = part.split('=')
        policy[subs[0]] = subs[1]
    return policy

