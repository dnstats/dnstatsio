from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Boolean, String, DateTime, ForeignKey, BigInteger, Text

Base = declarative_base()


class Run(Base):
    __tablename__ = 'runs'
    id = Column(BigInteger, primary_key=True)
    start_time = Column(DateTime)
    start_rank = Column(BigInteger)
    end_rank = Column(BigInteger)


class Site(Base):
    __tablename__ = 'sites'
    id = Column(BigInteger, primary_key=True)
    domain = Column(String)
    current_rank = Column(BigInteger)


class SiteRun(Base):
    __tablename__ = 'site_runs'
    id = Column(BigInteger, primary_key=True)
    site_id = Column(BigInteger, ForeignKey('sites.id'))
    run_id = Column(BigInteger, ForeignKey('runs.id'))
    run_rank = Column(BigInteger)
    caa_record = Column(Text)
    has_caa_reporting = Column(Boolean)
    has_dmarc = Column(Boolean)
    dmarc_policy = Column(Boolean)
    sub_dmarc_policy = Column(Boolean)
    has_dmarc_reporting = Column(Boolean)
    dmarc_policy_id = Column(BigInteger, ForeignKey('dmarc_policy.id'))
    dmarc_record = Column(Text)
    has_spf = Column(Boolean)
    spf_policy = Column(BigInteger, ForeignKey('spf_policy.id'))
    txt_records = Column(Text)
    ds_records = Column(Text)
    mx_records = Column(Text)


class SpfPolicy(Base):
    __tablename__ = 'spf_policy'
    id = Column(BigInteger, primary_key=True)
    qualifier = Column(String)
    display_name = Column(String)


class DmarcPolicy(Base):
    __tablename__ = 'dmarc_policy'
    id = Column(BigInteger, primary_key=True)
    policy_string = Column(String)
    display_name = Column(String)
