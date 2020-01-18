import csv

import dnstats.db.models as models
from dnstats.db import db_session


def seed_db() -> None:
    _seed_dmarc_policy()
    _seed_spf()
    _seed_email_providers()


def _seed_spf():
    spf_policies = [
        ('+all', 'Pass', '#FF00FF'),
        ('?all', 'Neutral', '#FFBF7F'),
        ('~all', 'Soft-fail', '#72e572'),
        ('-all', 'Fail', '#8080FF'),
        ('no_policy', 'No Policy', '#FF8080')
    ]

    for spf_pol in spf_policies:
        spf_policy = models.SpfPolicy(qualifier=spf_pol[0], display_name=spf_pol[1], color=spf_pol[2])
        db_session.add(spf_policy)
        db_session.commit()


def _seed_sites(filename):
    with open(filename, 'r') as file:
        csv_reader = csv.DictReader(file)

        for row in csv_reader:
            site = models.Site(current_rank=row['rank'], domain=row['site'])
            db_session.add(site)
            db_session.commit()


def _seed_dmarc_policy():
    dmarc_policies = [
        ('none', 'None', '#FFBF7F'),
        ('quarantine', 'Quarantine', '#FFBF7F'),
        ('reject', 'Reject', '#8080FF'),
        ('no_policy', 'No Policy', '#FF8080'),
        ('invalid', 'Invalid', '#FF00FF')
    ]
    for dmarc_pol in dmarc_policies:
        dmarc_policy = models.DmarcPolicy(policy_string=dmarc_pol[0], display_name=dmarc_pol[1], color=dmarc_pol[2])
        db_session.add(dmarc_policy)
        db_session.commit()

def _seed_email_providers():
    email_providers = [
        ("Google Apps", "l.google.com.", True),
        ("Office 365", "protection.outlook.", True),
        ("ProofPoint", "pphosted.com.", True),
        ("Minecast", "mimecast.com.", True),
        ("MailRoute", "mailroute.net.", True),
        ("Zoho", "zoho.com.", True),
        ("Barracuda Networks", "barracudanetworks.com.", True),
        ("FastMail", "messagingengine.com.", True),
        ("Cisco Cloud Email Security", "iphmx.com.", True),
        ("Self-Hosted", "domain.", False),
        ("Symantec Messaging Security", "messagelabs.com.", True),
        ("FireEyeCloud", "fireeyecloud.com.",True),
        ("ProofPoint Essentials", "ppe-hosted.com.", True),
        ("Amazon Web Services", "amazonaws.com.", True),
        ("DreamHost", "dreamhost.com.", True),
        ("Office 365", "eo.outlook.com.", True),
        ("OSU OpenSource Lab", "osuosl.org.", True),
        ("Gandi", "gandi.net.", True),
        ("Rackspace", "emailsrvr.com.", True),
        ("TrendMicro Hosted Email Security", "in.hes.trendmicro.com.", True),
        ("Self-Hosted", "amazon-smtp.amazon.com.", True),
        ("TrendMicro Hosted Email Security", "in.hes.trendmicro.eu.", True),
        ("Self-Hosted", "wikimedia.org.", True),
        ("GoDaddy", "secureserver.net.", True),
        ("NoMail", '{"0."}', True),
        ("QQ", "qq.com.", True),
        ("No mail", "nxdomain.", False),
    ]

    for email_provider in email_providers:
        email_provide = models.EmailProvider(display_name=email_provider[0], search_regex=email_provider[1],
                                             is_regex=email_provider[2])
        db_session.add(email_provide)
        db_session.commit()