import os
import time
import subprocess
import datetime
from jinja2 import Environment, FileSystemLoader

from dnstats.db import db_session, engine
from dnstats.db import models as models


def render_pie(categories, filename: str):
    # This method assumes that there is no file extension
    file_loader = FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates'))
    env = Environment(loader=file_loader)
    template = env.get_template('pie_charts.tex.j2')
    result = template.render(categories=categories)
    with open('{}.tex'.format(filename), 'w') as f:
        f.write(result)
    subprocess.run(['xelatex', filename])
    subprocess.run(['magick', 'convert', '-density', '3000', '-scale', 'x740', '{}.pdf'.format(filename),
                    '{}.png'.format(filename)])
    os.remove('{}.tex'.format(filename))
    os.remove('{}.log'.format(filename))
    os.remove('{}.aux'.format(filename))
    os.remove('{}.pdf'.format(filename))


def get_categories_from_query(run_id: int, query: str) -> [()]:
    # This method assumes that the count is in column 0, name of the group is in column 1, and color is in column 2
    categories = []
    with engine.connect() as connection:
        total_count = db_session.query(models.SiteRun).filter_by(run_id=run_id).count()
        result_set = connection.execute(query)

        for row in result_set:
            category = {'percent': round((row[0]/total_count) * 100, 1), 'name': row[1], 'color': row[2]}
            categories.append(category)
    return categories


def get_categories_from_adoption_query(run_id: int, query: str) -> [()]:
    categories = []
    with engine.connect() as connection:
        total_count = db_session.query(models.SiteRun).filter_by(run_id=run_id).count()
        result_set = connection.execute(query)
        for row in result_set:
            yes = round((row[0]/total_count), 1) * 100
            yes_count = row[0]
        no = round(((total_count - yes_count)/total_count), 1) * 100
        categories.append({'percent': yes, 'name': 'Yes', 'color': 'green'})
        categories.append({'percent': no, 'name': 'No', 'color': 'red'})
        return categories


def run_report(query: str, report: str, adoption: bool, run_id: int):
    if adoption:
        categories = get_categories_from_adoption_query(run_id, query)
    else:
        categories = get_categories_from_query(run_id, query)
    filename = _create_timedate_filename(report)
    render_pie(categories, filename)
    return filename, report


def _create_timedate_filename(basefilename: str) -> str:
    now = datetime.datetime.now()
    return '{}_{}'.format(now.strftime('%Y-%m-%d_%H_%M_%S'), basefilename)


def create_reports(run_id: int):
    spf_adoption_query = "select count(*) from site_runs sr where sr.run_id = {} and sr.has_spf is true".format(run_id)

    spf_reports_query = "select count(*), sp.display_name, sp.color from site_runs sr join spf_policy sp on sr.spf_policy_id = sp.id " \
                  "where sr.run_id = {} group by sp.display_name, sp.color".format(run_id)

    dmarc_adoption_query = "select count(*) from site_runs where run_id = {} and has_dmarc is true".format(run_id)

    dmarc_policy_query = "select count(*), dp.display_name, dp.color from site_runs sr " \
                         "join dmarc_policy dp on sr.dmarc_policy_id = dp.id where sr.run_id = {} " \
                         "group by dp.display_name, dp.color, dp.display_name".format(run_id)

    caa_adoption_query = "select count(*) from site_runs where run_id = {} and has_caa is true".format(run_id)

    caa_reporting = "select count(*) from site_runs where run_id = {} and has_caa_reporting is true".format(run_id)

    filenames = [run_report(spf_adoption_query, 'SPF Adoption', True, run_id),
                 run_report(spf_reports_query, 'SPF Policy', False, run_id),
                 run_report(dmarc_adoption_query, 'DMARC Adaption', True, run_id),
                 run_report(dmarc_policy_query, 'DMARC Policy', False, run_id),
                 run_report(caa_adoption_query, 'CAA Adoption', True, run_id),
                 run_report(caa_reporting, 'CAA Reporting', True, run_id)]

    create_html(filenames, run_id)


def create_html(filenames: [()], run_id: int):
    print(filenames)
    file_loader = FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates'))
    env = Environment(loader=file_loader)
    template = env.get_template('index.html.j2')
    run = db_session.query(models.Run).filter_by(id=run_id).one()
    report_date = run.start_time.strftime('%B %d, %Y')
    result = template.render(charts=filenames, report_date=report_date, end_rank=run.end_rank)
    filename = _create_timedate_filename('index') + '.html'
    with open(filename, 'w') as file:
        file.write(result)
