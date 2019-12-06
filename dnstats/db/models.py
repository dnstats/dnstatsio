from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Boolean, String, DateTime, ForeignKey, BigInteger, Text, UniqueConstraint

Base = declarative_base()


class DmarcPolicy(Base):
    __tablename__ = 'dmarc_policy'
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
    dmarc_policy = Column(Boolean, nullable=False)
    sub_dmarc_policy = Column(Boolean, nullable=False)
    has_dmarc_aggregate_reporting = Column(Boolean, nullable=False)
    has_dmarc_forensic_reporting = Column(Boolean, nullable=False)
    dmarc_policy_id = Column(BigInteger, ForeignKey('dmarc_policy.id'))
    dmarc_sub_policy_id = Column(BigInteger, ForeignKey('dmarc_policy.id'))
    dmarc_record = Column(Text)
    has_spf = Column(Boolean, nullable=False)
    spf_policy_id = Column(BigInteger, ForeignKey('spf_policy.id'), nullable=False)
    txt_records = Column(Text)
    ds_records = Column(Text)
    mx_records = Column(Text)
    ns_records = Column(Text)
    UniqueConstraint('site_id', 'run_id')

    def has_dmarc_reporting(self):
        return self.has_dmarc_aggregate_reporting or self.has_dmarc_forensic_reporting


class SpfPolicy(Base):
    __tablename__ = 'spf_policy'
    id = Column(BigInteger, primary_key=True)
    qualifier = Column(String, nullable=False)
    display_name = Column(String, nullable=False)
    color = Column(String, nullable=False)
    UniqueConstraint('policy_string')


class Color(Base):
    __timename__ = 'color'
    id = Column(BigInteger, primary_key=True)
    name = Column(String, nullable=True)
    UniqueConstraint('name')
