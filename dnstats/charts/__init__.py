import os
import socket
import datetime

from jinja2 import Environment, FileSystemLoader

from dnstats.db import db_session, engine
from dnstats.db import models as models
from dnstats.charts.asset_utils import slugify, calculate_sri_hash
from dnstats.charts.colors import get_color


def _render_piejs(categories, filename: str):
    file_loader = FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates'))
    env = Environment(loader=file_loader)
    template = env.get_template('charts.j2.js')
    result = template.render(categories=categories)
    with open('{}.js'.format(filename), 'w') as f:
        f.write(result)


def _get_categories_from_query(query: str, random_colors: bool) -> [()]:
    # This method assumes that the count is in column 0, name of the group is in column 1, and color is in column 2
    categories = []
    counter = 0
    with engine.connect() as connection:
        result_set = connection.execute(query)

        for row in result_set:
            if random_colors:
                color = get_color(counter)
                counter += 1
                categories.append({'value': row[0], 'name': row[1], 'color': color})
            else:
                categories.append({'value': row[0], 'name': row[1], 'color': row[2]})
    return categories


def _get_categories_from_adoption_query(run_id: int, query: str) -> [()]:
    categories = []
    with engine.connect() as connection:
        total_count = db_session.query(models.SiteRun).filter_by(run_id=run_id).count()
        result_set = connection.execute(query)
        for row in result_set:
            yes = row[0]
        no = total_count - yes
        categories.append({'value': yes, 'name': 'Yes', 'color': '#72e572'})
        categories.append({'value': no, 'name': 'No', 'color': '#FF8080'})
        return categories


def _run_report(query: str, report: str, adoption: bool, run_id: int, random_colors=False):
    if adoption:
        categories = _get_categories_from_adoption_query(run_id, query)
    else:
        categories = _get_categories_from_query(query, random_colors)
    filename = _create_time_date_filename(report)
    return filename, report, slugify(report), categories


def _create_time_date_filename(basefilename: str) -> str:
    now = datetime.datetime.now()
    return '{}_{}'.format(now.strftime('%Y-%m-%d_%H_%M_%S'), basefilename)


def create_reports(run_id: int):
    spf_adoption_query = "select count(*) from site_runs sr " \
                         "where sr.run_id = {} and sr.has_spf is true".format(run_id)

    spf_reports_query = "select count(*), sp.display_name, sp.color from site_runs sr " \
                        "join spf_policies sp on sr.spf_policy_id = sp.id " \
                        "where sr.run_id = {} " \
                        "group by sp.display_name, sp.color".format(run_id)

    dmarc_adoption_query = "select count(*) from site_runs where run_id = {} and has_dmarc is true".format(run_id)

    dmarc_policy_query = "select count(*), dp.display_name, dp.color from site_runs sr " \
                         "join dmarc_policies dp on sr.dmarc_policy_id = dp.id where sr.run_id = {} " \
                         "group by dp.display_name, dp.color, dp.display_name".format(run_id)

    caa_adoption_query = 'select count(*) from site_runs ' \
                         'where run_id = {} and has_caa is true'.format(run_id)

    caa_reporting = "select count(*) from site_runs " \
                    "where run_id = {} and has_caa_reporting is true".format(run_id)

    caa_has_wilcard = "select count(*) from site_runs where run_id = {} and caa_wildcard_count > 0".format(run_id)

    mx_query = 'select count(*) from site_runs ' \
               'where run_id = {} and mx_records is not null'.format(run_id)

    # TODO Get ids from database
    dmarc_sub_policy_adoption = 'select count(*) from site_runs sr ' \
                                'where run_id = {} ' \
                                'and (dmarc_sub_policy_id != 4 or dmarc_sub_policy_id = 5)'.format(run_id)

    dmarc_subpolicy_query = "select count(*), dp.display_name, dp.color from site_runs sr " \
                            "join dmarc_policies dp on sr.dmarc_sub_policy_id = dp.id where sr.run_id = {} " \
                            "group by dp.display_name, dp.color, dp.display_name".format(run_id)

    dnssec_adoption = "select count(*) from site_runs " \
                      "where run_id = {} and ds_records is not null".format(run_id)

    email_providers = "select count(*), display_name from site_runs sr " \
                      "join email_providers ep on sr.email_provider_id=ep.id " \
                      "where run_id={} " \
                      "group by display_name " \
                      "order by count asc;".format(run_id)

    dns_providers = "select count(*), display_name from site_runs sr " \
                      "join dns_providers dp on sr.dns_provider_id=dp.id " \
                      "where run_id={} " \
                      "group by display_name " \
                      "order by count asc;".format(run_id)

    caa_issue_count = """
                    select count(*), sr.range
                        from (select case
                                         when caa_issue_count = 0 then '0'
                                         when caa_issue_count = 1 then '1'
                                         when caa_issue_count > 1 and caa_issue_count <= 5 then '2-5'
                                         when caa_issue_count > 5 and caa_issue_count <= 10 then '6-10'
                                         when caa_issue_count > 10 then '11+' end as range
                              from site_runs sr where run_id = {}) as sr
                        group by sr.range

                """.format(run_id)

    caa_wildcard_issue_count = """
                    select count(*), sr.range
                        from (select case
                                         when caa_wildcard_count = 0 then '0'
                                         when caa_wildcard_count = 1 then '1'
                                         when caa_wildcard_count > 1 and caa_wildcard_count <= 5 then '2-5'
                                         when caa_wildcard_count > 5 and caa_wildcard_count <= 10 then '6-10'
                                         when caa_wildcard_count > 10 then '11+' end as range
                              from site_runs sr
                              where run_id = {}) as sr
                        group by sr.range

                """.format(run_id)

    category_data = [_run_report(spf_adoption_query, 'SPF Adoption', True, run_id),
                     _run_report(spf_reports_query, 'SPF Policy', False, run_id),
                     _run_report(dmarc_adoption_query, 'DMARC Adaption', True, run_id),
                     _run_report(dmarc_sub_policy_adoption, 'DMARC Subdomain Policy Adaption', True, run_id),
                     _run_report(dmarc_policy_query, 'DMARC Policy', False, run_id),
                     _run_report(dmarc_subpolicy_query, 'DMARC Subdomain Policy', False, run_id),
                     _run_report(mx_query, 'Has MX Records', True, run_id),
                     _run_report(caa_adoption_query, 'CAA Adoption', True, run_id),
                     _run_report(caa_reporting, 'CAA Reporting', True, run_id),
                     _run_report(dnssec_adoption, 'DNSSEC Adoption', True, run_id),
                     _run_report(email_providers, 'Email Providers', False, run_id, True),
                     _run_report(dns_providers, 'DNS Providers', False, run_id, True),
                     _run_report(caa_issue_count, 'CAA Issue Count', False, run_id, True),
                     _run_report(caa_wildcard_issue_count, 'CAA Wildcard Issue Count', False, run_id, True)
                     ]
    js_filename = _create_time_date_filename('charts')
    _render_piejs(category_data, js_filename)
    html_filename = _create_html(category_data, run_id, js_filename)
    return js_filename, html_filename


def _create_html(category_data: [()], run_id: int, js_filename: str):
    for filename in category_data:
        print(filename[1], filename[2])
    hostname = socket.gethostname()
    file_loader = FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates'))
    env = Environment(loader=file_loader)
    template = env.get_template('index.html')
    run = db_session.query(models.Run).filter_by(id=run_id).one()
    report_date = run.start_time.strftime('%B %d, %Y')
    js_sha = calculate_sri_hash(js_filename + '.js')
    end_rank = '{:,}'.format(run.end_rank)
    result = template.render(charts=category_data, report_date=report_date, end_rank=end_rank,
                             js_filename=js_filename,
                             js_sha=js_sha, hostname=hostname)
    filename = _create_time_date_filename('index') + '.html'
    with open(filename, 'w') as file:
        file.write(result)
    return filename
