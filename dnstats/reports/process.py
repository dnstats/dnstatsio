import json
import os
import pathlib

import dnstats.settings as settings
from dnstats.db import engine, db_session, models
from dnstats.utils.aws import s3_upload_string


def process_report(run_id: int, report: dict) -> None:
    _validate_report(report)
    data = _get_data(run_id, report)
    _upload(_create_csv(data), run_id, report, 'csv')
    _upload(json.dumps(data), run_id, report, 'json')


def _upload(data: str, run_id: int, report: dict, report_type: str) -> bool:
    run = db_session.query(models.Run).filter_by(id=run_id).one()
    filename = _get_file_name_from_run_id(run_id, report, report_type)
    if settings.UPLOAD_REPORTS:
        s3_upload_string(settings.REPORT_S3_BUCKET_NAME, filename, data)
    else:
        pathlib.Path(os.path.join(os.path.dirname(__file__), 'output', run.start_time.strftime("%Y/%m/%d/")).replace('dnstats/reports/', '')).mkdir(parents=True, exist_ok=True)
        path = os.path.join(os.path.dirname(__file__), 'output', filename).replace('dnstats/reports/', '')
        with open(path, 'w') as f:
            f.write(data)
    return True


def _get_file_name_from_run_id(run_id: int, report: dict, suffix: str):
    run = db_session.query(models.Run).filter_by(id=run_id).one()
    return run.start_time.strftime("%Y/%m/%d/{report_name}.{suffix}".format(report_name=report['name'], suffix=suffix))


def _create_csv(data: list) -> str:
    lines = list()
    lines.append('rank,domain')
    for row in data:
        lines.append('{rank},{domain}'.format(rank=row['rank'], domain=row['domain']))
    return '\n'.join(lines)


def _validate_report(report: dict) -> None:
    if 'query' not in report:
        raise ValueError("No report query defined")
    if 'name' not in report:
        raise ValueError("No report name defined")


def _get_data(run_id: int, report: dict) -> ({}):
    query = """select sr.run_rank, s.domain
           from site_runs sr
                     join sites s on sr.site_id = s.id
            where run_id = {run_id}
              and {query}
            order by sr.run_rank;
            """.format(run_id=run_id, query=report['query'])
    sites = list()
    with engine.connect() as connection:
        result_set = connection.execute(query)

        for row in result_set:
            sites.append({'rank': row[0], 'domain': row[1]})
    return sites
