import enum

from dnstats.db import db_session
import dnstats.db.models as models
from dnstats.dnsutils.dnssec import Algorithm, Digest, ALGORITHM_MUST_NOT, ALGORITHM_SHOULD_NOT


class DnsSecErrors(enum.Enum):
    NO_DS_RECORDS = 0
    NO_DNSKEY_RECORD = 1
    FORBIDDEN_DS_ALGORITHM = 2
    NOT_RECOMMENDED_DS_ALGORITHM = 3
    WEAK_DIGEST = 4
    FORBIDDEN_DNSKEY_ALGORITHM = 5
    NOT_RECOMMENDED_DNSKEY_ALGORITHM = 6
    INVALID_DNSKEY_RECORD = 7


class DnsSec:
    def __init__(self, run_id: int, domain: str):
        self.run_id = run_id
        self.domain = domain

    @property
    def errors(self) -> list:
        return _validate_dnssec(self.run_id, self.domain)['errors']


def _validate_dnssec(run_id: int, domain: str) -> dict:
    site = db_session.query(models.Site).filter_by(domain=domain)
    last_run = db_session.query(models.Site).filter_by(site_id=site.id, run_id=run_id).one()
    errors = list()
    no_dnssec = False
    if not last_run.ds_record:
        errors.append(DnsSecErrors.NO_DS_RECORDS)
        no_dnssec = True

    if not last_run.dnskey:
        errors.append(DnsSecErrors.NO_DNSKEY_RECORD)
        no_dnssec = True

    if no_dnssec:
        return {'errors': errors}

    ds_algorithm = Algorithm(last_run.dnssec_ds_algorithm)

    if ds_algorithm in ALGORITHM_MUST_NOT:
        errors.append(DnsSecErrors.FORBIDDEN_DS_ALGORITHM)

    if ds_algorithm in ALGORITHM_SHOULD_NOT:
        errors.append(DnsSecErrors.NOT_RECOMMENDED_DS_ALGORITHM)

    dnskey_algorithm = Algorithm(last_run.dnssec_dnskey_algorithm)

    if dnskey_algorithm in ALGORITHM_MUST_NOT:
        errors.append(DnsSecErrors.FORBIDDEN_DNSKEY_ALGORITHM)

    if dnskey_algorithm in ALGORITHM_SHOULD_NOT:
        errors.append(DnsSecErrors.NOT_RECOMMENDED_DNSKEY_ALGORITHM)

    digest = Digest(last_run.dnssec_digest_type)

    if digest == Digest.SHA1:
        errors.append(DnsSecErrors.WEAK_DIGEST)

    for dnskey in last_run.dnskey_records.split(','):
        parts = dnskey.split(' ', 3)
        if len(parts) != 4:
            errors.append(DnsSecErrors.INVALID_DNSKEY_RECORD)
            continue
        key = parts[3].replace(' ', '')

    result = dict()
    result['errors'] = errors
    result['ds_algorithm'] = ds_algorithm
    result['dnskey_algorithm'] = dnskey_algorithm
    result['digest'] = digest
    return result
