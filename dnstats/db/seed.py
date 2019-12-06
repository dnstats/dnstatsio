import csv

import dnstats.db.models as models
from dnstats.db import db_session


def seed_db(filename: str) -> None:
    _seed_dmarc_policy()
    _seed_sites(filename)
    _seed_spf()


def _seed_spf():
    spf_policies = [
        ('+all', 'Pass', 'magenta'),
        ('?all', 'Neutral', 'orange'),
        ('~all', 'Soft-fail', 'green'),
        ('-all', 'Fail', 'blue'),
        ('no_policy', 'No Policy', 'red')
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
        ('none', 'None', 'orange'),
        ('quarantine', 'Quarantine', 'green'),
        ('reject', 'Reject', 'blue'),
        ('no_policy', 'No Policy', 'red')
    ]
    for dmarc_pol in dmarc_policies:
        dmarc_policy = models.DmarcPolicy(policy_string=dmarc_pol[0], display_name=dmarc_pol[1], color=dmarc_pol[2])
        db_session.add(dmarc_policy)
        db_session.commit()
