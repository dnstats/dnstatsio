from celery import Celery, Task

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
def site_stat(site: str, rank: int, run_id: int):
    mail = dnutils.safe_query(site, 'mx')
    txt = dnutils.safe_query(site, 'txt')
    caa = dnutils.safe_query(site, 'caa')
    ds = dnutils.safe_query(site, 'ds')
    dmarc = dnutils.safe_query('_dmarc.' + site, 'txt')

    return site, rank, run_id, caa, dmarc, mail, txt, ds


@app.task(base=SqlAlchemyTask)
def process_result(site, rank, run_id, caa, dmarc, mail, txt, ds):
    as_dmarc_aggregate, has_dmarc_forensic, has_dmarc, dmarc_policy, dmarc_sub_policy = dnutils.get_dmarc_stats(dmarc)
    dmarc_policy_db = db_session.query(models.DmarcPolicy).filter(policy_string=dmarc_policy)
    sub_dmarc_policy_db = db_session.query(models.DmarcPolicy).filter(policy_string=dmarc_sub_policy)
    has_caa_reporting = dnutils.caa_has_iodef(caa)
    is_spf, spf_record, spf_policy = dnutils.get_spf_stats(txt)
    sr = models.SiteRun(site_id=site, run_id=run_id, run_rank=rank, caa_record=caa, has_caa_reporting=has_caa_reporting,
                        has_dmarc=has_dmarc, dmarc_policy=dmarc_policy_db, sub_dmarc_policy=sub_dmarc_policy_db)
    return
