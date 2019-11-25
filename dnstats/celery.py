from celery import Celery, Task
from celery.canvas import group, chain
from sqlalchemy import and_

import dnstats.dnsutils as dnutils
import dnstats.db.models as models
from dnstats.db import db_session

app = Celery('dnstats', broker='amqp://guest@localhost//')


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
    dmarc = dnutils.safe_query('_dmarc.' + site, 'txt')

    return site, site.current_rank, run_id, caa, dmarc, mail, txt, ds


@app.task(base=SqlAlchemyTask)
def process_result(site_id: int, rank: int, run_id, caa, dmarc, mail, txt, ds):
    has_dmarc_aggregate, has_dmarc_forensic, has_dmarc, dmarc_policy, dmarc_sub_policy = dnutils.get_dmarc_stats(dmarc)
    dmarc_policy_db = db_session.query(models.DmarcPolicy).filter(policy_string=dmarc_policy)
    sub_dmarc_policy_db = db_session.query(models.DmarcPolicy).filter(policy_string=dmarc_sub_policy)
    has_caa_reporting = dnutils.caa_has_iodef(caa)
    is_spf, spf_record, spf_policy = dnutils.get_spf_stats(txt)
    sr = models.SiteRun(site_id=site_id, run_id=run_id, run_rank=rank, caa_record=caa, has_caa_reporting=has_caa_reporting,
                        has_dmarc=has_dmarc, dmarc_policy=dmarc_policy_db, sub_dmarc_policy=sub_dmarc_policy_db)
    db_session.add(sr)
    db_session.commit()
    return


@app.task()
def launch_run(run_id):
    run = db_session.query(models.Run).filter(models.Run.id==id).scalar()
    sites = db_session.query(models.Site).filter(and_(models.Site.current_rank > run.start_rank, models.Site.current_rank < run.end_rank))
    group(chain(site_stat.s(site.id, run.id), process_result.s()) for site in sites)
