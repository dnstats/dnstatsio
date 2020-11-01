import dns.resolver

from dnstats.db import models
from dnstats.db import db_session


def safe_query(site: str, type: str):
    r = None
    try:
        r = dns.resolver.query(site, type)
    except:
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
    return {'caa_issue_count': issue_count, 'caa_wildcard_count': wildcard_count, 'caa_has_reporting': has_reporting,
            'caa_allows_wildcard': allows_wildcard, 'caa_exists': has_caa}


def get_dmarc_stats(ans):
    aggregate = False
    forensic = False
    dmarc = False
    policy = ""
    sub_policy = ""
    if ans:
        for r in ans:
            if r.startswith('"v=DMARC1'):
                if dmarc:
                    policy = 'invalid'
                    break
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
                break

    if policy is '':
        policy = 'no_policy'
    if sub_policy is '':
        sub_policy = 'no_policy'
    return {'dmarc_has_aggregate': aggregate, 'dmarc_has_forensic': forensic, 'dmarc_exists': dmarc,
            'dmarc_policy': policy, 'dmarc_sub_policy': sub_policy}


def _parse_dmarc(record) -> []:
    record = record.replace('"', '')
    if not record.startswith('v=DMARC1'):
        return []
    parts = record.split(';')
    policy = dict()
    for part in parts:
        subs = part.split('=')
        if len(subs) == 2:
            policy[subs[0].strip()] = subs[1].strip()
    return policy


def get_provider_from_ns_records(ans: list, site: str) -> int:
    if ans:
        ns_string = ''.join(ans).lower()
        if ns_string.endswith(site + '.'):
            return db_session.query(models.DnsProvider).filter_by(search_regex='Self-hosted').one().id
        providers = db_session.query(models.DnsProvider).filter_by(is_regex=True).all()
        for provider in providers:
            if provider.search_regex in ns_string:
                return provider.id
        return db_session.query(models.DnsProvider).filter_by(search_regex='Unknown.').one().id


def is_a_msft_dc(domain: str) -> bool:
    ans = safe_query('_msdcs.{}'.format(domain), 'soa')
    if ans and len(ans) > 0:
        rand_ans = safe_query('88DkwqpKw01OP7O.{}'.format(domain), 'soa')
        rand_result = rand_ans and len(rand_ans) > 0
        if not rand_result:
            return True
    else:
        return False

