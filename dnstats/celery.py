import datetime
import os

from celery import Celery, Task
from celery.canvas import chain, group
from celery.schedules import crontab
from celery.utils.log import get_task_logger
from sqlalchemy import and_
from sqlalchemy.sql.expression import func

import dnstats.charts
from dnstats.utils.grading import _grade_errors, get_site_and_site_run
from dnstats.utils.site_import import setup_import_list
import dnstats.dnsutils as dnutils
import dnstats.dnsutils.spf as spfutils
import dnstats.dnsutils.mx as mxutils
import dnstats.db.models as models
from dnstats.dnsutils.dnssec import parse_ds, parse_dnskey
from dnstats.dnsutils.ns import get_name_server_ips, get_name_server_results
from dnstats.db import db_session, engine
from dnstats.utils import chunks
from dnstats.httputils import has_security_txt
from dnstats.grading.spf import grade as grade_spf_record
from dnstats.grading.dmarc import grade as grade_dmarc_record
from dnstats.grading.caa import grade as grade_caa_records
from dnstats.grading.ns import grade as grade_ns_records
from dnstats.grading.soa import grade as grade_soa_records
from dnstats.reports.process import process_report as process_report_main
from dnstats import settings
from dnstats.utils import check_for_config, setup_sentry
from dnstats.utils.email import _send_botched_deploy, _send_eoq, _send_published_email, _send_start_email, _send_sites_updated_done

check_for_config()

app = Celery('dnstats', broker=settings.AMQP, backend=settings.CELERY_BACKEND, broker_pool_limit=50)

logger = get_task_logger('dnstats.scans')

setup_sentry()


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(crontab(hour=1, minute=1), import_list.s())
    sender.add_periodic_task(crontab(hour=8, minute=0), do_run.s())
    sender.add_periodic_task(crontab(hour=18, minute=0), do_charts_latest.s())
    sender.add_periodic_task(crontab(hour=18, minute=15), do_reports_latest.s())


class SqlAlchemyTask(Task):
    """An abstract Celery Task that ensures that the connection the the
    database is closed on task completion

    From: http://www.prschmid.com/2013/04/using-sqlalchemy-with-celery-tasks.html
    """
    abstract = True

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        db_session.remove()
        super(SqlAlchemyTask, self).after_return(status, retval, task_id, args, kwargs, einfo)


@app.task(queue='deployment')
def do_charts(run_id: int):
    run = db_session.query(models.Run).filter_by(id=run_id).scalar()
    if not settings.DNSTATS_ENV == 'Development':
        target = 920000
        site_run_count = db_session.query(models.SiteRun).filter_by(run_id=run_id).count()
        if site_run_count < target:
            _send_botched_deploy(run.start_time, site_run_count, site_run_count, target)
            return
    folder_name = run.start_time.strftime("%Y-%m-%d")
    js_filename, html_filename = dnstats.charts.create_reports(run_id)
    print(js_filename)
    print(html_filename)
    if settings.DNSTATS_ENV == 'Development':
        return
    os.system("ssh dnstatsio@www.dnstats.io 'mkdir /home/dnstatsio/public_html/{}'".format(folder_name))
    os.system('scp {filename}.js dnstatsio@www.dnstats.io:/home/dnstatsio/public_html/{folder_name}/{filename}.js'.format(filename=js_filename, folder_name=folder_name))
    os.system('scp {filename} dnstatsio@www.dnstats.io:/home/dnstatsio/public_html/{folder_name}/index.html'.format(filename=html_filename, folder_name=folder_name))
    os.system("ssh dnstatsio@www.dnstats.io 'rm /home/dnstatsio/public_html/index.html'")
    os.system("ssh dnstatsio@www.dnstats.io 'ln -s /home/dnstatsio/public_html/{folder_name}/index.html /home/dnstatsio/public_html/index.html'".format(folder_name=folder_name, filename=html_filename))
    os.system("ssh dnstatsio@www.dnstats.io 'ln -s /home/dnstatsio/public_html/{folder_name}/{filename}.js /home/dnstatsio/public_html/'".format(folder_name=folder_name, filename=js_filename))
    _send_published_email(run_id)


@app.task(queue='deployment')
def do_charts_latest():
    the_time = db_session.query(func.Max(models.Run.start_time)).scalar()
    run = db_session.query(models.Run).filter_by(start_time=the_time).scalar()
    do_charts.s(run.id).apply_async()


@app.task(time_limit=530, soft_time_limit=500, queue='gevent')
def site_stat(site_id: int, run_id: int):
    logger.debug('start site stat site {} run id {}'.format(site_id, run_id))
    result = dict()
    result['start_time'] = datetime.datetime.now()
    site = db_session.query(models.Site).filter(models.Site.id == site_id).scalar()
    logger.debug('got site for {}'.format(site.domain))
    result['mx'] = dnutils.safe_query(site.domain, 'mx')
    logger.debug('got mx for {}'.format(site.domain))
    result['txt'] = dnutils.safe_query(site.domain, 'txt')
    logger.debug('got txtf or {}'.format(site.domain))
    result['caa'] = dnutils.safe_query(site.domain, 'caa')
    logger.debug('got caa for {}'.format(site.domain))
    result['ds'] = dnutils.safe_query(site.domain, 'ds')
    result['dnskey'] = dnutils.safe_query(site.domain, 'dnskey')
    logger.debug('got dnskey for {}'.format(site.domain))
    result['ns'] = dnutils.safe_query(site.domain, 'ns')
    logger.debug('got ns')
    result['dmarc'] = dnutils.safe_query('_dmarc.' + site.domain, 'txt')
    logger.debug('got dmarc for {}'.format(site.domain))
    result['has_dnssec'] = None
    logger.debug('got security.txt for {}'.format(site.domain))
    result['is_msdcs'] = dnstats.dnsutils.is_a_msft_dc(site.domain)
    logger.debug('got has msdc for {}'.format(site.domain))
    result['site_id'] = site.id
    logger.debug('set site id {}'.format(site.domain))
    result['rank'] = site.current_rank
    logger.debug('set rank {}'.format(site.domain))
    result['run_id'] = run_id
    logger.debug('set run id {} -- done'.format(site.domain))
    result['name_server_ips'] = get_name_server_ips(result['ns'])
    logger.debug('got the IP addresses for all the name servers')
    result['ns_server_ns_results'] = get_name_server_results(result['name_server_ips'], site.domain)
    logger.debug('got name server results from each name server')
    result['soa'] = dnutils.safe_query(site.domain, 'soa')
    logger.debug('got soa for {}'.format(site.domain))
    result['end_time'] = datetime.datetime.now()
    return result


@app.task(time_limit=60, soft_time_limit=54)
def process_result(result: dict):
    logger.debug("Processing site: {}".format(result['site_id']))
    processed = dict()
    site = db_session.query(models.Site).filter_by(id=result['site_id']).one()
    processed.update(dnutils.get_dmarc_stats(result['dmarc']))
    dmarc_policy_db = db_session.query(models.DmarcPolicy).filter_by(policy_string=processed['dmarc_policy']).scalar()
    if dmarc_policy_db is None:
        dmarc_policy_db = db_session.query(models.DmarcPolicy).filter_by(policy_string='invalid').scalar()
    sub_dmarc_policy_db = db_session.query(models.DmarcPolicy).filter_by(policy_string=processed['dmarc_sub_policy']).scalar()
    if sub_dmarc_policy_db is None:
        sub_dmarc_policy_db = db_session.query(models.DmarcPolicy).filter_by(policy_string='invalid').scalar()
    processed.update(dnutils.caa_stats(result['caa']))
    processed.update(spfutils.get_spf_stats(result['txt']))
    spf_db = db_session.query(models.SpfPolicy).filter_by(qualifier=processed['spf_policy']).scalar()
    processed['email_provider_id'] = mxutils.get_provider_from_mx_records(result['mx'], site.domain)
    processed['dns_provider_id'] = dnutils.get_provider_from_ns_records(result['ns'], site.domain)
    processed.update(parse_ds(result['ds']))
    processed['dnssec_dnskey_algorithm'] = parse_dnskey(result['dnskey'])
    sr = models.SiteRun(site_id=result['site_id'], run_id=result['run_id'], run_rank=result['rank'], caa_record=result['caa'], has_caa=processed['caa_exists'],
                        has_caa_reporting=processed['caa_has_reporting'], caa_issue_count=processed['caa_issue_count'], caa_wildcard_count=processed['caa_wildcard_count'],
                        has_dmarc=processed['dmarc_exists'], dmarc_policy_id=dmarc_policy_db.id,
                        dmarc_sub_policy_id=sub_dmarc_policy_db.id, has_dmarc_aggregate_reporting=processed['dmarc_has_aggregate'],
                        has_dmarc_forensic_reporting=processed['dmarc_has_forensic'], dmarc_record=result['dmarc'], has_spf=processed['spf_exists'],
                        spf_policy_id=spf_db.id, txt_records=result['txt'], ds_records=result['ds'], mx_records=result['mx'],
                        ns_records=result['ns'], email_provider_id=processed['email_provider_id'], dns_provider_id=processed['dns_provider_id'],
                        dnssec_ds_algorithm=processed['ds_algorithm'], dnssec_digest_type=processed['ds_digest_type'],
                        dnssec_dnskey_algorithm=processed['dnssec_dnskey_algorithm'], has_securitytxt=result['has_dnssec'], has_msdc=result['is_msdcs'],
                        j_caa_records=result['caa'], j_dmarc_record=result['dmarc'], j_txt_records=result['txt'],
                        j_ns_records=result['ns'], j_mx_records=result['mx'], j_ds_recoreds=result['ds'],
                        ns_ip_addresses=result['name_server_ips'], ns_server_ns_results=result['ns_server_ns_results'],
                        j_soa_records=result['soa'])
    db_session.add(sr)
    db_session.commit()
    do_grading(sr)


@app.task(time_limit=320, soft_time_limit=300)
def grade_spf(site_run_id: int):
    site, site_run = get_site_and_site_run(site_run_id)
    records = site_run.j_txt_records
    grade, errors = grade_spf_record(records, site.domain, site_run.has_mx)
    site_run.spf_grade = grade
    db_session.commit()
    _grade_errors(errors, 'spf', site_run_id)


@app.task(time_limit=80, soft_time_limit=75)
def grade_dmarc(site_run_id: int):
    site, site_run = get_site_and_site_run(site_run_id)
    records = site_run.j_dmarc_record
    grade = 0
    dmarcs = list()
    if records:
        for record in records:
            record = record.replace('"', '')
            if record.startswith('v=DMARC1;'):
                logger.debug('DMARC - {} - {}'.format(site_run_id, record))
                dmarcs.append(record)
        if dmarcs:
            logger.debug('DMARC Count - {} - {}'.format(site_run_id, len(dmarcs)))
            grade, errors = grade_dmarc_record(dmarcs, site.domain)
            _grade_errors(errors, 'dmarc', site_run_id)
    site_run.dmarc_grade = grade
    db_session.commit()


@app.task(time_limit=80, soft_time_limit=75)
def grade_caa(site_run_id: int):
    site, site_run = get_site_and_site_run(site_run_id)
    records = site_run.j_caa_records
    grade = 0
    if not records:
        logger.debug("CAA Grade: {} - {} - {} - NO CAA".format(site.domain, site_run.caa_grade, 0))
        grade = 0
    else:
        logger.debug("CAA Grade: {} - {} - {}".format(site.domain, site_run.caa_grade, grade))
        grade, errors = grade_caa_records(records, site.domain)
        _grade_errors(errors, 'caa', site_run_id)

    site_run.caa_grade = grade
    db_session.commit()


@app.task(time_limit=80, soft_time_limit=75)
def grade_ns(site_run_id: int) -> None:
    site, site_run = get_site_and_site_run(site_run_id)
    records = site_run.j_ns_records
    ip_addresses = site_run.ns_ip_addresses
    record_results = site_run.ns_server_ns_results
    grade = 0

    if not records:
        logger.debug("NS Grade: {} - {} - {} - NO CAA".format(site.domain, site_run.ns_grade, 0))
        grade = 0
    else:
        logger.debug("NS Grade: {} - {} - {}".format(site.domain, site_run.ns_grade, grade))
        grade, errors = grade_ns_records(records, ip_addresses, record_results, site.domain)
        _grade_errors(errors, 'ns', site_run_id)
    site_run.ns_grade = grade
    db_session.commit()


@app.task(time_limit=80, soft_time_limt=75)
def grade_soa(site_run_id: int) -> None:
    site, site_run = get_site_and_site_run(site_run_id)
    records = site_run.j_soa_records
    grade = 0
    if not records:
        logger.debug("SOA Grade: {} - {} - {} - NO CAA".format(site.domain, site_run.ns_grade, 0))
        grade = 0
    else:
        logger.debug("SOA Grade: {} - {} - {}".format(site.domain, site_run.ns_grade, grade))
        grade, errors = grade_soa_records(records, site.domain)
        _grade_errors(errors, 'soa', site_run_id)
    site_run.soa_grade = grade
    db_session.commit()


@app.task()
def launch_run(run_id):
    logger.warning("Launching run {}".format(run_id))
    run = db_session.query(models.Run).filter(models.Run.id == run_id).scalar()
    sites = db_session.query(models.Site).filter(and_(models.Site.current_rank >= run.start_rank,
                                                      models.Site.current_rank <= run.end_rank))

    sites_all_chunked = list(chunks(sites.all(), 10000))
    c = 0
    for sites in sites_all_chunked:
        g = group(chain(site_stat.s(site.id, run.id), process_result.s()) for site in sites).apply_async()
        print(c)
        c += 1
    _send_eoq(run_id)


@app.task()
def do_run():
    date = datetime.datetime.now()
    if settings.DNSTATS_ENV == 'Development':
        run = models.Run(start_time=date, start_rank=1, end_rank=150)
        logger.warning("[DO RUN]: Running a Debug top 50 sites runs")
    else:
        run = models.Run(start_time=date, start_rank=1, end_rank=1000000)
        logger.warning("[DO RUN]: Running a normal run of top 1,000,000 sites runs")
    db_session.add(run)
    db_session.commit()
    run = db_session.query(models.Run).filter_by(start_time=date).first()
    _send_start_email(date, run.id)
    launch_run(run.id)


@app.task
def import_list():
    new_sites = setup_import_list(logger)

    existing_sites = dict()
    with engine.connect() as connection:
        logger.warning("Getting current sites")
        result = connection.execute("select domain, current_rank from sites")
        for row in result:
            existing_sites[row[0]] = row[1]
        run_rank_site(existing_sites, new_sites)
        chunk_count = 0
        sites_chunked_new = {}
        sites_chunked_update = {}
        for site in new_sites.keys():
            if site in existing_sites:
                if existing_sites[site] != new_sites[site]:
                    sites_chunked_update[site] = new_sites[site]
                    if len(sites_chunked_update) >= 100:
                        chunk_count += 1
                        # loop counter to monitor task creation status
                        logger.debug("existing_sites chunk count: {}".format(chunk_count))
                        logger.info("Creating update task: {}".format(chunk_count))
                        _update_site_rank_chunked.s(dict(sites_chunked_update)).apply_async()
                        sites_chunked_update.clear()
            else:
                sites_chunked_new[site] = new_sites[site]
                if len(sites_chunked_new) >= 100:
                    chunk_count += 1
                    # loop counter to monitor task creation status
                    logger.debug("sites_chunked_new: {}".format(chunk_count))
                    logger.info("Creating new site task: {}".format(chunk_count))
                    _process_new_sites_chunked.s(dict(sites_chunked_new)).apply_async()
                    sites_chunked_new.clear()
        if len(sites_chunked_new) > 0:
            _process_new_sites_chunked.s(sites_chunked_new).apply_async()
        if len(sites_chunked_update) > 0:
            _update_site_rank_chunked.s(sites_chunked_update).apply_async()
        logger.warning("Site import task creation complete")

    _send_sites_updated_done()


@app.task()
def _unrank_domain(domain: str):
    site = db_session.query(models.Site).filter_by(domain=domain).first()
    if site:
        site.current_rank = 0
        db_session.commit()
        logger.debug("Unranking site: {}".format(domain))


@app.task()
def _process_new_site(domain: bytes, new_rank: int) -> None:
    site = db_session.query(models.Site).filter_by(domain=domain).first()
    if site:
        site.current_rank = new_rank
    else:
        site = models.Site(domain=str(domain), current_rank=new_rank)
        db_session.add(site)
        logger.debug("Adding site: {}".format(domain))
    db_session.commit()


@app.task()
def _process_new_sites_chunked(domains_ranked: dict) -> None:
    for domain in domains_ranked.keys():
        site = models.Site(domain=str(domain), current_rank = domains_ranked[domain])
        db_session.add(site)
        logger.debug("Adding site: {}".format(domain))
    db_session.commit()
    logger.info("New site chunk updated")


@app.task()
def _update_site_rank_chunked(domains_ranked: dict) -> None:
    for domain in domains_ranked.keys():
        site = db_session.query(models.Site).filter_by(domain=domain).first()
        if site.current_rank != domains_ranked[domain]:
            site.current_rank = domains_ranked[domain]
            logger.debug("Updating site rank: {}".format(domain))
    db_session.commit()
    logger.info("Site rank chunk updated")

@app.task
def do_reports_latest():
    the_time = db_session.query(func.Max(models.Run.start_time)).scalar()
    run = db_session.query(models.Run).filter_by(start_time=the_time).scalar()
    publish_reports.s(run.id).apply_async()

@app.task
def publish_reports(run_id: int):
    # sr is the alias for site_runs table
    reports = list()
    reports.append({'query': 'sr.mx_records is not null', 'name': 'mx_domains', 'type': 'list'})
    reports.append({'query': 'sr.mx_records is null', 'name': 'no_mx_domains', 'type': 'list'})

    reports.append({'query': 'sr.dnssec_ds_algorithm != -1', 'name': 'dnssec_domains', 'type': 'list'})
    reports.append({'query': 'sr.dnssec_ds_algorithm = -1', 'name': 'no_dnssec_domains', 'type': 'list'})

    reports.append({'query': 'sr.has_caa is true', 'name': 'caa_domains', 'type': 'list'})
    reports.append({'query': 'sr.has_caa is not true', 'name': 'no_caa_domains', 'type': 'list'})

    reports.append({'query': 'sr.has_caa_reporting is true', 'name': 'caa_reporting_domains', 'type': 'list'})
    reports.append({'query': 'sr.has_caa_reporting is not true', 'name': 'no_caa_reporting_domains', 'type': 'list'})

    reports.append({'query': 'sr.has_dmarc is true', 'name': 'dmarc_domains', 'type': 'list'})
    reports.append({'query': 'sr.has_dmarc is not true', 'name': 'no_dmarc_domains'})

    reports.append({'query': 'sr.dmarc_policy_id = 1', 'name': 'dmarc_none', 'type': 'list'})
    reports.append({'query': 'sr.dmarc_policy_id = 2', 'name': 'dmarc_quarantine', 'type': 'list'})
    reports.append({'query': 'sr.dmarc_policy_id = 3', 'name': 'dmarc_reject', 'type': 'list'})
    reports.append({'query': 'sr.dmarc_policy_id = 4', 'name': 'dmarc_no_policy', 'type': 'list'})
    reports.append({'query': 'sr.dmarc_policy_id = 5', 'name': 'dmarc_invalid', 'type': 'list'})

    reports.append({'query': 'sr.has_spf is true', 'name': 'spf_domains', 'type': 'list'})
    reports.append({'query': 'sr.has_spf is not true', 'name': 'no_spf_domains', 'type': 'list'})

    reports.append({'query': 'sr.spf_policy_id = 1', 'name': 'spf_pass', 'type': 'list'})
    reports.append({'query': 'sr.spf_policy_id = 2', 'name': 'spf_neutral', 'type': 'list'})
    reports.append({'query': 'sr.spf_policy_id = 3', 'name': 'spf_softfail', 'type': 'list'})
    reports.append({'query': 'sr.spf_policy_id = 4', 'name': 'spf_fail', 'type': 'list'})
    reports.append({'query': 'sr.spf_policy_id = 5', 'name': 'spf_no_policy', 'type': 'list'})

    reports.append({'query': 'sr.has_securitytxt is true', 'name': 'securitytxt_domains', 'type': 'list'})
    reports.append({'query': 'sr.has_securitytxt is not true', 'name': 'no_securitytxt_domains', 'type': 'list'})

    for report in reports:
        process_report.s(run_id, report).apply_async()


@app.task
def process_report(run_id: int, report: dict):
    process_report_main(run_id, report)

def do_grading(sr):
    grade_spf.s(sr.id).apply_async()
    grade_dmarc.s(sr.id).apply_async()
    grade_caa.s(sr.id).apply_async()
    grade_ns.s(sr.id).apply_async()
    grade_soa.s(sr.id).apply_async()

def run_rank_site(existing_sites, new_sites):
    unranked_sites = existing_sites.keys() - new_sites.keys()
    for site in unranked_sites:
        _unrank_domain.s(str(site)).apply_async()
        logger.debug("Unranking site: {}".format(site))
