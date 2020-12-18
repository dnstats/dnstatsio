import json
import os


import dnstats.settings as settings
from dnstats.db import engine, db_session, models
from dnstats.utils.aws import s3_upload


def process_report(run_id: int, report: dict -> None):
    _validate_report(report)
    data = _get_data(run_id, report)
    _upload(_create_csv(data), run_id, report, 'csv')
    _upload(json.dups(data), run_id, report, 'json')

def _upload(data: str, run_id: int, report: dict, report_type: str) -> bool:
    filename = _get_file_name_from_run_id(run_id, report, report_type)
    if settings.UPLOAD_REPORTs:
        s3_upload()
    else:
        path = os.path.join('output', filename)
        with file(path, 'w') as f:
            f.write(data)
    return True


def _get_file_name_from_run_id(run_id: str, report: dict, suffix: str)
    run = db_session.query(models.Run).filter_by(id=run_id.one()
    return run.start_time.strptime("%Y/%m/%d/{report_name}.{suffix}".format(report_name=report['name'], suffix))

def _create_csv(data: list) -> str:
    lines = list()
    lines.append('rank,domain')
    for row in data:
        lines.append('{rank},{domain}'.format(rank=row['rank'], row['domain'])
    return '\n'.join(lines)

def _valid_report(report: dict) -> None:
    if query not in report:
      raise ValueError("No report query defined")
    if name not in report:
      raise ValueError("No report name defined")



def _get_data(run_id: int, report: dict -> ({}):
    query = """select sr.run_rank, s.domain
           from site_runs sr
                     join sites s on sr.site_id = s.id
            where run_id = {run_id}
              and {query}
            order by sr.run_rank;
            """.format(run_id=run_id, query=query)
    sites = list()
    with engine.connect() as connection:
        result_set = connection.execute(query)
    
        for row in result_set:
            sites.append({'rank': row[0], 'domain': row[1]})
    return sites

