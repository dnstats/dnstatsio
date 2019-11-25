import csv

import dnstats.db.models as models
from dnstats.db import db_session


def seed_db(filename: str) -> None:
    with open(filename, 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            site = models.Sites(current_rank=row['rank'], domain=row['site'])
            db_session.add(site)
            db_session.commit()
