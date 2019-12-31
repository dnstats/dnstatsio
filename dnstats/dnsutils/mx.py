from dnstats.db import models
from dnstats.db import db_session
from dnstats.dnsutils import safe_query


def get_provider_from_mx_records(ans: list, site: str):
    if ans:
        mx_string = ''.join(ans)
        providers = db_session.query(models.EmailProvider).filter_by(is_regex=True).all()
        if mx_string.endswith(site + '.'):
            return db_session.query(models.EmailProvider).filter_by(display_name='Self-Hosted').one().id
        for provider in providers:
            if provider.search_regex in mx_string:
                return provider.id

def test(site: str):
    ans = safe_query(site, 'mx')
    print(get_provider_from_mx_records(ans, site))