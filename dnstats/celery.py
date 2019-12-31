from celery import Celery, Task
from celery.canvas import group, chain
from celery.utils.log import get_task_logger
from sqlalchemy import and_

import dnstats.dnsutils as dnutils
import dnstats.dnsutils.spf as spfutils
import dnstats.dnsutils.mx as mxutils
import dnstats.db.models as models
from dnstats.db import db_session

app = Celery('dnstats', broker='amqp://guest@localhost//')

logger = get_task_logger('dnstats.scans')


class SqlAlchemyTask(Task):
    """An abstract Celery Task that ensures that the connection the the
    database is closed on task completion

    From: http://www.prschmid.com/2013/04/using-sqlalchemy-with-celery-tasks.html
    """
    abstract = True

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        db_session.remove()


@app.task()
def site_stat(site_id: int, run_id: int):
    site = db_session.query(models.Site).filter(models.Site.id==site_id).scalar()
    mail = dnutils.safe_query(site.domain, 'mx')
    txt = dnutils.safe_query(site.domain, 'txt')
    caa = dnutils.safe_query(site.domain, 'caa')
    ds = dnutils.safe_query(site.domain, 'ds')
    ns = dnutils.safe_query(site.domain, 'ns')
    dmarc = dnutils.safe_query('_dmarc.' + site.domain, 'txt')

    return [site.id, site.current_rank, run_id, caa, dmarc, mail, txt, ds, ns]


@app.task(base=SqlAlchemyTask)
def process_result(result):
    logger.warn(result[0])
    site = db_session.query(models.Site).filter_by(id=result[0]).one()
    has_dmarc_aggregate, has_dmarc_forensic, has_dmarc, dmarc_policy, dmarc_sub_policy = dnutils.get_dmarc_stats(result[4])
    dmarc_policy_db = db_session.query(models.DmarcPolicy).filter_by(policy_string=dmarc_policy).scalar()
    sub_dmarc_policy_db = db_session.query(models.DmarcPolicy).filter_by(policy_string=dmarc_sub_policy).scalar()
    issue_count, wildcard_count, has_reporting, allows_wildcard, has_caa = dnutils.caa_stats(result[3])
    is_spf, spf_record, spf_policy = spfutils.get_spf_stats(result[6])
    spf_db = db_session.query(models.SpfPolicy).filter_by(qualifier=spf_policy).scalar()
    mx_db = mxutils.get_provider_from_mx_records(result[5], site.domain)
    sr = models.SiteRun(site_id=result[0], run_id=result[2], run_rank=result[1], caa_record=result[3], has_caa=has_caa,
                        has_caa_reporting=has_reporting, caa_issue_count=issue_count, caa_wildcard_count=wildcard_count,
                        has_dmarc=has_dmarc, dmarc_policy_id=dmarc_policy_db.id,
                        dmarc_sub_policy_id=sub_dmarc_policy_db.id, has_dmarc_aggregate_reporting=has_dmarc_aggregate,
                        has_dmarc_forensic_reporting=has_dmarc_forensic, dmarc_record=result[4], has_spf=is_spf,
                        spf_policy_id=spf_db.id, txt_records=result[6], ds_records=result[7], mx_records=result[5],
                        ns_records=result[8], email_provider_id=mx_db)
    db_session.add(sr)
    db_session.commit()
    return


@app.task()
def launch_run(run_id):
    run = db_session.query(models.Run).filter(models.Run.id == run_id).scalar()
    sites = db_session.query(models.Site).filter(and_(models.Site.current_rank >= run.start_rank, models.Site.current_rank <= run.end_rank))
    group(chain(site_stat.s(site.id, run.id), process_result.s()) for site in sites).apply_async()
