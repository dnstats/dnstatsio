from dnstats.db import models
from dnstats.db import db_session
from dnstats.dnsutils import safe_query


def get_provider_from_mx_records(ans: list, site: str) -> int:
    if ans:
        mx_string = ''.join(ans).lower()
        providers = db_session.query(models.EmailProvider).filter_by(is_regex=True).all()
        if mx_string.endswith(site + '.'):
            return db_session.query(models.EmailProvider).filter_by(search_regex='domain.').one().id
        for provider in providers:
            if provider.search_regex in mx_string:
                return provider.id
        return db_session.query(models.EmailProvider).filter_by(search_regex='Unknown.').one().id
    else:
        return db_session.query(models.EmailProvider).filter_by(search_regex='nxdomain.').one().id


def test(site: str):
    ans = safe_query(site, 'mx')
    print(get_provider_from_mx_records(ans, site))
