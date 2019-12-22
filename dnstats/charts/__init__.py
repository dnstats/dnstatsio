import os
import subprocess
import datetime
import hashlib
import base64

from jinja2 import Environment, FileSystemLoader

from dnstats.db import db_session, engine
from dnstats.db import models as models


def _render_pie(categories, filename: str):
    # This method assumes that there is no file extension
    file_loader = FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates'))
    env = Environment(loader=file_loader)
    template = env.get_template('pie_charts.tex.j2')
    result = template.render(categories=categories)
    with open('{}.tex'.format(filename), 'w') as f:
        f.write(result)
    subprocess.run(['latex', '{}.tex'.format(filename)])
    subprocess.run(['dvisvgm', '{}.dvi'.format(filename)])
    os.rename('{}-1.svg'.format(filename), '{}.svg'.format(filename))
    _replace_black('{}.svg'.format(filename))


def _render_piejs(categories, filename: str):
    file_loader = FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates'))
    env = Environment(loader=file_loader)
    template = env.get_template('charts.j2.js')
    result = template.render(categories=categories)
    with open('{}.js'.format(filename), 'w') as f:
        f.write(result)


def get_categories_from_query(run_id: int, query: str) -> [()]:
    # This method assumes that the count is in column 0, name of the group is in column 1, and color is in column 2
    categories = []
    with engine.connect() as connection:
        result_set = connection.execute(query)

        for row in result_set:
            category = {'value': row[0], 'name': row[1], 'color': row[2]}
            categories.append(category)
    return categories


def get_categories_from_adoption_query(run_id: int, query: str) -> [()]:
    categories = []
    with engine.connect() as connection:
        total_count = db_session.query(models.SiteRun).filter_by(run_id=run_id).count()
        result_set = connection.execute(query)
        for row in result_set:
            yes = row[0]
        no = total_count - yes
        categories.append({'value': yes, 'name': 'Yes', 'color': 'green'})
        categories.append({'value': no, 'name': 'No', 'color': 'red'})
        return categories


def run_report(query: str, report: str, adoption: bool, run_id: int):
    if adoption:
        categories = get_categories_from_adoption_query(run_id, query)
    else:
        categories = get_categories_from_query(run_id, query)
    filename = _create_timedate_filename(report)
    # _render_pie(categories, filename)
    return filename, report, _slugify(report),  categories


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

    caa_adoption_query = 'select count(*) from site_runs where run_id = {} and has_caa is true'.format(run_id)

    caa_reporting = "select count(*) from site_runs where run_id = {} and has_caa_reporting is true".format(run_id)

    mx_query = 'select count(*) from site_runs where run_id = {} and mx_records is not null'.format(run_id)

    dmarc_sub_policy_adoption = 'select count(*) from site_runs sr where run_id = {} ' \
                                'and (dmarc_sub_policy_id != 4 or dmarc_sub_policy_id = 5)'.format(run_id)

    dmarc_subpolicy_query = "select count(*), dp.display_name, dp.color from site_runs sr " \
                            "join dmarc_policy dp on sr.dmarc_sub_policy_id = dp.id where sr.run_id = {} " \
                            "group by dp.display_name, dp.color, dp.display_name".format(run_id)

    filenames = [run_report(spf_adoption_query, 'SPF Adoption', True, run_id),
                 run_report(spf_reports_query, 'SPF Policy', False, run_id),
                 run_report(dmarc_adoption_query, 'DMARC Adaption', True, run_id),
                 run_report(dmarc_sub_policy_adoption, 'DMARC Subdomain Policy Adaption', True, run_id),
                 run_report(dmarc_policy_query, 'DMARC Policy', False, run_id),
                 run_report(dmarc_subpolicy_query, 'DMARC Subdomain Policy', False, run_id),
                 run_report(mx_query, 'Has MX Records', True, run_id),
                 run_report(caa_adoption_query, 'CAA Adoption', True, run_id),
                 run_report(caa_reporting, 'CAA Reporting', True, run_id), ]
    js_filename = _create_timedate_filename('charts')
    _render_piejs(filenames, js_filename)
    create_html(filenames, run_id, js_filename)


def create_html(filenames: [()], run_id: int, js_filename: str):
    print(filenames)
    file_loader = FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates'))
    env = Environment(loader=file_loader)
    template = env.get_template('index.html.j2')
    run = db_session.query(models.Run).filter_by(id=run_id).one()
    report_date = run.start_time.strftime('%B %d, %Y')
    result = template.render(charts=filenames, report_date=report_date, end_rank=run.end_rank, js_filename=js_filename)
    filename = _create_timedate_filename('index') + '.html'
    with open(filename, 'w') as file:
        file.write(result)


def _replace_black(filename: str):
    with open(filename, 'r') as file:
        svgdata = file.read()

    svgdata = svgdata.replace("stroke='#000'", "stroke='#fff'")

    with open(filename, 'w') as file:
        file.write(svgdata)


def _slugify(input_str: str) -> str:
    return input_str.replace(' ', '_').lower()


def calculate_sri_hash(filename: str):
    hashing = hashlib.sha3_384()
    with open(filename, 'rb') as file:
        chunk = file.read(hashing.block_size)
        hashing.update(chunk)
    return base64.b64encode(hashing.hexdigest())
