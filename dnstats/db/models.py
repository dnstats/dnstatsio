from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Boolean, String, DateTime, ForeignKey, BigInteger, Text, UniqueConstraint, SmallInteger, JSON

Base = declarative_base()


class DmarcPolicy(Base):
    __tablename__ = 'dmarc_policies'
    id = Column(BigInteger, primary_key=True)
    policy_string = Column(String, nullable=False)
    display_name = Column(String, nullable=False)
    color = Column(String, nullable=False)
    UniqueConstraint('policy_string')


class Run(Base):
    __tablename__ = 'runs'
    id = Column(BigInteger, primary_key=True)
    start_time = Column(DateTime, nullable=False)
    start_rank = Column(BigInteger, nullable=False)
    end_rank = Column(BigInteger, nullable=False)


class Site(Base):
    __tablename__ = 'sites'
    id = Column(BigInteger, primary_key=True)
    domain = Column(String, nullable=False)
    current_rank = Column(BigInteger, nullable=False)
    UniqueConstraint('domain')


class SiteRun(Base):
    __tablename__ = 'site_runs'
    id = Column(BigInteger, primary_key=True)
    site_id = Column(BigInteger, ForeignKey('sites.id'), nullable=False)
    run_id = Column(BigInteger, ForeignKey('runs.id'), nullable=False)
    run_rank = Column(BigInteger, nullable=False)
    caa_record = Column(Text)
    has_caa = Column(Boolean, nullable=False)
    has_caa_reporting = Column(Boolean, nullable=False)
    caa_issue_count = Column(BigInteger)
    caa_wildcard_count = Column(BigInteger)
    has_dmarc = Column(Boolean, nullable=False)
    has_dmarc_aggregate_reporting = Column(Boolean, nullable=False)
    has_dmarc_forensic_reporting = Column(Boolean, nullable=False)
    dmarc_policy_id = Column(BigInteger, ForeignKey('dmarc_policies.id'))
    dmarc_sub_policy_id = Column(BigInteger, ForeignKey('dmarc_policies.id'))
    dmarc_record = Column(Text)
    has_spf = Column(Boolean, nullable=False)
    spf_policy_id = Column(BigInteger, ForeignKey('spf_policies.id'), nullable=False)
    txt_records = Column(Text)
    ds_records = Column(Text)
    mx_records = Column(Text)
    ns_records = Column(Text)
    email_provider_id = Column(BigInteger, ForeignKey('email_providers.id'))
    dns_provider_id = Column(BigInteger, ForeignKey('dns_providers.id'))
    dnssec_ds_algorithm = Column(SmallInteger)
    dnssec_digest_type = Column(SmallInteger)
    dnssec_dnskey_algorithm = Column(SmallInteger)
    has_securitytxt = Column(Boolean)
    has_msdc = Column(Boolean)
    spf_grade = Column(BigInteger)
    dmarc_grade = Column(BigInteger)
    caa_grade = Column(BigInteger)
    j_caa_records = Column(JSON)
    j_txt_records = Column(JSON)
    j_dmarc_record = Column(JSON)

    UniqueConstraint('site_id', 'run_id')

    def has_dmarc_reporting(self):
        return self.has_dmarc_aggregate_reporting or self.has_dmarc_forensic_reporting

    def has_mx(self) -> bool:
        return self.mx_records is not None


class SpfPolicy(Base):
    __tablename__ = 'spf_policies'
    id = Column(BigInteger, primary_key=True)
    qualifier = Column(String, nullable=False)
    display_name = Column(String, nullable=False)
    color = Column(String, nullable=False)
    UniqueConstraint('policy_string')


class EmailProvider(Base):
    __tablename__ = 'email_providers'
    id = Column(BigInteger, primary_key=True)
    display_name = Column(String, nullable=False)
    search_regex = Column(String, nullable=False)
    is_regex = Column(Boolean, nullable=False, default=True)
    UniqueConstraint('search_regex')


class DnsProvider(Base):
    __tablename__ = 'dns_providers'
    id = Column(BigInteger, primary_key=True)
    display_name = Column(String, nullable=False)
    search_regex = Column(String, nullable=False)
    is_regex = Column(Boolean, nullable=False, default=True)
    UniqueConstraint('search_regex')


class RemarkTypes(Base):
    __tablename__ = 'remark_types'
    id = Column(SmallInteger, primary_key=True)
    name = Column(String, nullable=False)
    UniqueConstraint('name')


class Remark(Base):
    __tablename__ = 'remarks'
    id = Column(SmallInteger, primary_key=True)
    name = Column(String, nullable=False)
    remark_type_id = Column(SmallInteger, ForeignKey('remark_types.id'))
    remark_level = Column(SmallInteger)


class SiteRunRemark(Base):
    __tablename__ = 'siterun_remarks'
    id = Column(BigInteger, primary_key=True)
    site_run_id = Column(BigInteger, ForeignKey('site_runs.id'))
    remark_id = Column(SmallInteger, ForeignKey('remarks.id'))
