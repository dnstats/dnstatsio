from dnstats.celery import process_report



def do_reports(run_id: int):
    # sr is the alias for site_runs table
    reports = list()
    reports.append({'query': 'sr.mx_records is not null', 'title': 'mx_domains'})
    reports.append({'query': 'sr.mx_records is null', 'title': 'no_mx_domains'})
    reports.append({'query': 'sr.caa is true', 'title': 'caa_domains'})
    reports.append({'query': 'sr.caa is not true', 'title': 'no_caa_domains'})

    for report in reports:
        process_report.s(run_id, report).apply_async()
