import datetime
import os

from sendgrid import SendGridAPIClient, Mail

from db import db_session, models as models
import dnstats.settings as settings



def _send_message(email):
    if settings.DNSTATS_ENV == 'Development':
        print(email)
        return

    sendgrid = SendGridAPIClient(settings.DNSTATS_ENV)
    sendgrid.send(email)


def _send_start_email(date, run_id):
    subject = '[DNStats] Scan Starting'
    body = '''
    Starting time: {starting_time}
    Run id: {run_id}
    DNStats scan is starting to queue sites.




    
    
    '''.format(starting_time=date.strftime('%c'), run_id=run_id)
    message = Mail(from_email='worker@dnstats.io', to_emails='dnstats_cron@dnstats.io', subject=subject,
                   plain_text_content=body)
    _send_message(message)


def _send_eos(results, run_time):
    subject = '[DNStats] Scan Ending'
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
    subject = '[DNStats] All Scans In Queue'
    body = '''
    Run start time: {starting_time}
    Run id: {run_id}
    DNStats scan is in progress and the queuing process is done.
    

    
    
    
    
    
    '''.format(starting_time=run.start_time, run_id=run.id)
    message = Mail(from_email='worker@dnstats.io', to_emails='dnstats_cron@dnstats.io', subject=subject,
                   plain_text_content=body)
    _send_message(message)


def _send_published_email(run_id: int):
    subject = '[DNStats] Scan id {} Has Been Published'.format(run_id)
    body = '''
    The stats are now published at https://dnstats.io.
    
    
    
    
    
    
    
    
    '''
    message = Mail(from_email='worker@dnstats.io', to_emails='dnstats_cron@dnstats.io', subject=subject,
                   plain_text_content=body)
    _send_message(message)


def _send_sites_updated_started():
    subject = '[DNStats] Site List Update Started'
    body ="""
        Started site list upgrade at: {}
        
        
        
        
        
        
        
        
    """.format(datetime.datetime.now().strftime('%c'))
    message = Mail(from_email='worker@dnstats.io', to_emails='dnstats_cron@dnstats.io', subject=subject,
                   plain_text_content=body)
    _send_message(message)


def _send_sites_updated_done():
    subject = '[DNStats] Site List Update Is Done'
    body ="""
        Ended site list upgrade at: {}
        
        
        
        
        
        
        
        
        
        
    """.format(datetime.datetime.now().strftime('%c'))
    message = Mail(from_email='worker@dnstats.io', to_emails='dnstats_cron@dnstats.io', subject=subject,
                   plain_text_content=body)
    _send_message(message)


def _send_botched_deploy(date, run_id: int, count: int, target_count: int):
    delta = target_count - count
    subject = '[DNStats] CRITICAL Botched Website Deploy'
    body = '''
    Run id: {run_id}
    Target: {target_count}
    Actual = {count}
    Delta = {delta}
    Run start Time = {starting_time}
    Cowardly refusing to deploy run {run_id}, it appears the scan failed or is not finished. Investigate and publish 
    results.
    '''.format(starting_time=date.strftime('%c'), run_id=run_id, target_count=target_count, count=count, delta=delta)
    message = Mail(from_email='worker@dnstats.io', to_emails='dnstats_cron@dnstats.io', subject=subject,
                   plain_text_content=body)
    _send_message(message)