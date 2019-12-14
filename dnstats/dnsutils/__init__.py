import dns.resolver


def safe_query(site: str, type: str):
    r = None
    try:
        r = dns.resolver.query(site, type)
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers):
        pass

    if r:
        results = list()
        for ans in r:
            results.append(ans.to_text())
        return results
    else:
        return None


def caa_stats(ans):
    has_reporting = False
    has_caa = False
    allows_wildcard = False
    issue_count = 0
    wildcard_count = 0
    if ans:
        for r in ans:
            if ' iodef ' in r:
                has_reporting = True
            if ' issuewild ':
                allows_wildcard = True
                wildcard_count += 1
            if ' issue ' in r:
                has_caa = True
                issue_count += 1
    return issue_count, wildcard_count, has_reporting, allows_wildcard, has_caa


def get_dmarc_stats(ans):
    aggregate = False
    forensic = False
    dmarc = False
    policy = ""
    sub_policy = ""
    if ans:
        for r in ans:
            if r.startswith('"v=DMARC1'):
                dmarc = True
                dmarc_keys = _parse_dmarc(r)

                if 'rua' in dmarc_keys:
                    aggregate = True
                if "ruf" in dmarc_keys:
                    forensic = True
                if "p" in dmarc_keys:
                    policy = dmarc_keys['p']
                if 'sp' in dmarc_keys:
                    sub_policy = dmarc_keys['sp']
                continue
            else:
                policy = 'invalid'
    if policy is '':
        policy = 'no_policy'
    if sub_policy is '':
        sub_policy = 'no_policy'
    return aggregate, forensic, dmarc, policy, sub_policy


def _parse_dmarc(record) -> []:
    record = record.replace('"', '')
    if not record.startswith('v=DMARC1'):
        return []
    parts = record.split(';')
    policy = dict()
    for part in parts:
        subs = part.split('=')
        if len(subs) == 2:
            policy[subs[0].strip()] = subs[1]
    return policy