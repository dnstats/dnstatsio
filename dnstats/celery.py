import datetime
import io
import os
import zipfile

from celery import Celery, Task
from celery.canvas import chain, group
from celery.schedules import crontab
from celery.utils.log import get_task_logger
import requests
from sqlalchemy import and_
from sqlalchemy.sql.expression import func
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail



import dnstats.dnsutils as dnutils
import dnstats.dnsutils.spf as spfutils
import dnstats.dnsutils.mx as mxutils
from dnstats.dnsutils.dnssec import parse_ds, parse_dnskey
import dnstats.db.models as models
import dnstats.charts
from dnstats.db import db_session, engine
from dnstats.utils import chunks
from dnstats.httputils import has_security_txt

if not os.environ.get('DB'):
    raise EnvironmentError("Database connection is not setup.")

if not os.environ.get('AMQP'):
    raise EnvironmentError("Celery AMQP connection is not setup.")

if not os.environ.get('CELERY_BACKEND'):
    raise EnvironmentError("Celery CELERY_BACKEND connection is not setup.")


app = Celery('dnstats', broker=os.environ.get('AMQP'), backend=os.environ.get('CELERY_BACKEND'))

logger = get_task_logger('dnstats.scans')

if os.environ.get('DNSTATS_ENV') != 'Development':
    import sentry_sdk
    from sentry_sdk.integrations.celery import CeleryIntegration
    sentry_sdk.init(os.environ.get("SENTRY_URL"), integrations=[CeleryIntegration()])

app.conf.task_routes = {
                        'dnstats.celery.import_list': {'queue': 'prefork0'},
                        'dnstats.celery._process_new_site': {'queue': 'prefork0'},
                        'dnstats.celery._process_new_sites_chunked': {'queue': 'prefork0'},
                        'dnstats.celery._unrank_domain': {'queue': 'prefork0'},
                        }


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(crontab(hour=0, minute=58), import_list.s())
    sender.add_periodic_task(crontab(hour=8, minute=0), do_run.s())
    sender.add_periodic_task(crontab(hour=13, minute=0), do_charts_latest.s())


class SqlAlchemyTask(Task):
    """An abstract Celery Task that ensures that the connection the the
    database is closed on task completion

    From: http://www.prschmid.com/2013/04/using-sqlalchemy-with-celery-tasks.html
    """
    abstract = True

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        db_session.remove()
        super(SqlAlchemyTask, self).after_return(status, retval, task_id, args, kwargs, einfo)


@app.task()
def do_charts(run_id: int):
    run = db_session.query(models.Run).filter_by(id=run_id).scalar()
    folder_name = run.start_time.strftime("%Y-%m-%d")
    js_filename, html_filename = dnstats.charts.create_reports(run_id)
    print(js_filename)
    print(html_filename)
    if os.environ.get('DNSTATS_ENV') == 'Development':
        return
    os.system("ssh dnstatsio@www.dnstats.io 'mkdir /home/dnstatsio/public_html/{}'".format(folder_name))
    os.system('scp {filename}.js  dnstatsio@www.dnstats.io:/home/dnstatsio/public_html/{folder_name}/{filename}.js'.format(filename=js_filename, folder_name=folder_name))
    os.system('scp {filename}  dnstatsio@www.dnstats.io:/home/dnstatsio/public_html/{folder_name}/index.html'.format(filename=html_filename, folder_name=folder_name))
    os.system("ssh dnstatsio@www.dnstats.io 'rm /home/dnstatsio/public_html/index.html'")
    os.system("ssh dnstatsio@www.dnstats.io 'ln -s /home/dnstatsio/public_html/{folder_name}/index.html /home/dnstatsio/public_html/index.html'".format(folder_name=folder_name, filename=html_filename))
    os.system("ssh dnstatsio@www.dnstats.io 'ln -s /home/dnstatsio/public_html/{folder_name}/{filename}.js /home/dnstatsio/public_html/'".format(folder_name=folder_name, filename=js_filename))
    _send_published_email(run_id)


@app.task()
def do_charts_latest():
    the_time = db_session.query(func.Max(models.Run.start_time)).scalar()
    run = db_session.query(models.Run).filter_by(start_time=the_time).scalar()
    do_charts.s(run.id).apply_async()


@app.task(time_limit=420, soft_time_limit=400)
def site_stat(site_id: int, run_id: int):
    result = dict()
    site = db_session.query(models.Site).filter(models.Site.id == site_id).scalar()
    result['mx'] = dnutils.safe_query(site.domain, 'mx')
    result['txt'] = dnutils.safe_query(site.domain, 'txt')
    result['caa'] = dnutils.safe_query(site.domain, 'caa')
    result['ds'] = dnutils.safe_query(site.domain, 'ds')
    result['dnskey'] = dnutils.safe_query(site.domain, 'dnskey')
    result['ns'] = dnutils.safe_query(site.domain, 'ns')
    result['dmarc'] = dnutils.safe_query('_dmarc.' + site.domain, 'txt')
    result['has_dnssec'] = has_security_txt(site.domain)
    result['is_msdcs'] = dnstats.dnsutils.is_a_msft_dc(site.domain)
    result['site_id'] = site.id
    result['rank'] = site.current_rank
    result['run_id'] = run_id

    return result


@app.task(time_limit=60, soft_time_limit=54)
def process_result(result: dict):
    logger.warn(result['site_id'])
    site = db_session.query(models.Site).filter_by(id=result['site_id']).one()
    has_dmarc_aggregate, has_dmarc_forensic, has_dmarc, dmarc_policy, dmarc_sub_policy = dnutils.get_dmarc_stats(result['dmarc'])
    dmarc_policy_db = db_session.query(models.DmarcPolicy).filter_by(policy_string=dmarc_policy).scalar()
    if dmarc_policy_db is None:
        dmarc_policy_db = db_session.query(models.DmarcPolicy).filter_by(policy_string='invalid').scalar()
    sub_dmarc_policy_db = db_session.query(models.DmarcPolicy).filter_by(policy_string=dmarc_sub_policy).scalar()
    if sub_dmarc_policy_db is None:
        sub_dmarc_policy_db = db_session.query(models.DmarcPolicy).filter_by(policy_string='invalid').scalar()
    issue_count, wildcard_count, has_reporting, allows_wildcard, has_caa = dnutils.caa_stats(result['caa'])
    is_spf, spf_record, spf_policy = spfutils.get_spf_stats(result['txt'])
    spf_db = db_session.query(models.SpfPolicy).filter_by(qualifier=spf_policy).scalar()
    mx_db = mxutils.get_provider_from_mx_records(result['mx'], site.domain)
    dns_db = dnutils.get_provider_from_ns_records(result['ns'], site.domain)
    ds_algorithm, ds_digest_type = parse_ds(result['ds'])
    dnssec_dnskey_algorithm = parse_dnskey(result['dnskey'])
    sr = models.SiteRun(site_id=result['site_id'], run_id=result['run_id'], run_rank=result['rank'], caa_record=result['caa'], has_caa=has_caa,
                        has_caa_reporting=has_reporting, caa_issue_count=issue_count, caa_wildcard_count=wildcard_count,
                        has_dmarc=has_dmarc, dmarc_policy_id=dmarc_policy_db.id,
                        dmarc_sub_policy_id=sub_dmarc_policy_db.id, has_dmarc_aggregate_reporting=has_dmarc_aggregate,
                        has_dmarc_forensic_reporting=has_dmarc_forensic, dmarc_record=result['dmarc'], has_spf=is_spf,
                        spf_policy_id=spf_db.id, txt_records=result['txt'], ds_records=result['ds'], mx_records=result['mx'],
                        ns_records=result['ns'], email_provider_id=mx_db, dns_provider_id=dns_db,
                        dnssec_ds_algorithm=ds_algorithm, dnssec_digest_type=ds_digest_type,
                        dnssec_dnskey_algorithm=dnssec_dnskey_algorithm, has_securitytxt=result['has_dnssec'], has_msdc=result['is_msdcs'])
    db_session.add(sr)
    db_session.commit()
    return


@app.task()
def launch_run(run_id):
    logger.debug("Launching run {}".format(run_id))
    run = db_session.query(models.Run).filter(models.Run.id == run_id).scalar()
    sites = db_session.query(models.Site).filter(and_(models.Site.current_rank >= run.start_rank,
                                                      models.Site.current_rank <= run.end_rank))

    sites_all_chunked = list(chunks(sites.all(), 10000))
    for sites in sites_all_chunked:
        group(chain(site_stat.s(site.id, run.id), process_result.s()) for site in sites).apply_async()
    _send_eoq(run_id)


@app.task()
def do_run():
    date = datetime.datetime.now()
    if os.environ.get('DNSTATS_ENV') == 'Development':
        run = models.Run(start_time=date, start_rank=1, end_rank=150)
        logger.error("[DO RUN]: Running a Debug top 50 sites runs")
    else:
        run = models.Run(start_time=date, start_rank=1, end_rank=1000000)
        logger.error("[DO RUN]: Running a normal run of top 1,000,000 sites runs")
    db_session.add(run)
    db_session.commit()
    run = db_session.query(models.Run).filter_by(start_time=date).first()
    _send_start_email(date, run.id)
    launch_run(run.id)


@app.task
def import_list():
    _send_sites_updated_started()
    url = "https://tranco-list.eu/top-1m.csv.zip"
    r = requests.get(url)
    csv_content = zipfile.ZipFile(io.BytesIO(r.content)).read('top-1m.csv').splitlines()
    new_sites = dict()
    existing_sites = dict()
    for row in csv_content:
        row = row.split(b',')
        new_sites[str(row[1], 'utf-8')] = int(row[0])

    with engine.connect() as connection:
        logger.warn("Getting sites")
        result = connection.execute("select domain, current_rank from sites")
        for row in result:
            existing_sites[row[0]] = row[1]
        unranked_sites = existing_sites.keys() - new_sites.keys()
        for site in unranked_sites:
            _unrank_domain.s(str(site)).apply_async()
            logger.warn("Unranking site: {}".format(site))
        chunk_count = 0
        sites_chunked_new = {}
        sites_chunked_update = {}
        for site in new_sites.keys():
            if site in existing_sites:
                if existing_sites[site] != new_sites[site]:
                    sites_chunked_update[site] = new_sites[site]
                    if len(sites_chunked_update) >= 100:
                        chunk_count += 1
                        print(chunk_count)  # loop counter to monitor task creation status
                        _update_site_rank_chunked.s(dict(sites_chunked_update)).apply_async()
                        sites_chunked_update.clear()
            else:
                sites_chunked_new[site] = new_sites[site]
                if len(sites_chunked_new) >= 100:
                    chunk_count += 1
                    print(chunk_count)  # loop counter to monitor task creation status
                    _process_new_sites_chunked.s(dict(sites_chunked_new)).apply_async()
                    sites_chunked_new.clear()
        if len(sites_chunked_new) > 0:
            _process_new_sites_chunked.s(sites_chunked_new).apply_async()
        if len(sites_chunked_update) > 0:
            _update_site_rank_chunked.s(sites_chunked_update).apply_async()

    _send_sites_updated_done()


@app.task()
def _unrank_domain(domain: str):
    site = db_session.query(models.Site).filter_by(domain=domain).first()
    if site:
        site.current_rank = 0
        db_session.commit()


@app.task()
def _process_new_site(domain: bytes, new_rank: int) -> None:
    site = db_session.query(models.Site).filter_by(domain=domain).first()
    if site:
        site.current_rank = new_rank
    else:
        site = models.Site(domain=str(domain), current_rank=new_rank)
        db_session.add(site)
        logger.warn("Adding site: {}".format(domain))
    db_session.commit()


@app.task()
def _process_new_sites_chunked(domains_ranked: dict) -> None:
    for domain in domains_ranked.keys():
        site = models.Site(domain=str(domain), current_rank = domains_ranked[domain])
        db_session.add(site)
        logger.warn("Adding site: {}".format(domain))
    db_session.commit()


@app.task()
def _update_site_rank_chunked(domains_ranked: dict) -> None:
    for domain in domains_ranked.keys():
        site = db_session.query(models.Site).filter_by(domain=domain).first()
        if site.current_rank != domains_ranked[domain]:
            site.current_rank = domains_ranked[domain]
            logger.warn("Updating site rank: {}".format(domain))
    db_session.commit()


def _send_message(email):
    if os.environ.get('DNSTATS_ENV') == 'Development':
        print(email)
        return

    sendgrid = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
    sendgrid.send(email)


def _send_start_email(date, run_id):
    subject = 'DNStats Scan Starting'
    body = '''
    Starting time: {starting_time}
    Run id: {run_id}
    DNStats scan is starting to queue sites.




    
    
    '''.format(starting_time=date.strftime('%c'), run_id=run_id)
    message = Mail(from_email='worker@dnstats.io', to_emails='dnstats_cron@dnstats.io', subject=subject,
                   plain_text_content=body)
    _send_message(message)


@app.task
def _send_eos(results, run_time):
    subject = 'DNStats Scan Ending'
    print("taco")
    print(run_time)
    result_count = db_session.query(models.SiteRun).filter_by(run_id=run_time).count()
    print("result_count: " + str(result_count))
    body = '''
    End time: {starting_time}
    Number results: {result_count}
    Run id: {run_id}
    DNStats scan has ended.
    
    
    
    
    
    
    '''.format(starting_time=datetime.datetime.now().strftime('%c'), result_count=result_count, run_id=run_time)
    message = Mail(from_email='worker@dnstats.io', to_emails='dnstats_cron@dnstats.io', subject=subject,
                   plain_text_content=body)
    _send_message(message)
    print("body: " + body)


def _send_eoq(run_id):
    run = db_session.query(models.Run).filter_by(id=run_id).first()
    subject = 'DNStats All Scans In Queue'
    body = '''
    Run start time: {starting_time}
    Run id: {run_id}
    DNStats scan is in progress and the queuing process is done.
    

    
    
    
    
    
    '''.format(starting_time=run.start_time, run_id=run.id)
    message = Mail(from_email='worker@dnstats.io', to_emails='dnstats_cron@dnstats.io', subject=subject,
                   plain_text_content=body)
    _send_message(message)


def _send_published_email(run_id: int):
    subject = 'DNStats scan id {} has been published'.format(run_id)
    body = '''
    The stats are now published at https://dnstats.io.
    
    
    
    
    
    
    
    
    '''
    message = Mail(from_email='worker@dnstats.io', to_emails='dnstats_cron@dnstats.io', subject=subject,
                   plain_text_content=body)
    _send_message(message)


def _send_sites_updated_started():
    subject = 'DNStats Site List Update Started'
    body ="""
        Started site list upgrade at: {}
        
        
        
        
        
        
        
        
    """.format(datetime.datetime.now().strftime('%c'))
    message = Mail(from_email='worker@dnstats.io', to_emails='dnstats_cron@dnstats.io', subject=subject,
                   plain_text_content=body)
    _send_message(message)


def _send_sites_updated_done():
    subject = 'DNStats Site List Update Is Done'
    body ="""
        Ended site list upgrade at: {}
        
        
        
        
        
        
        
        
        
        
    """.format(datetime.datetime.now().strftime('%c'))
    message = Mail(from_email='worker@dnstats.io', to_emails='dnstats_cron@dnstats.io', subject=subject,
                   plain_text_content=body)
    _send_message(message)
