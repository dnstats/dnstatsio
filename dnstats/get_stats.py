import dns.resolver
from time import sleep
import csv
import re


def get_dns():
    with open('dnstats/sites_rank2.csv', 'r') as sites_file:

        with open('dnstats/dns_results.csv', 'w') as results_files:
            csv_reader = csv.DictReader(sites_file)
            fieldnames = ['rank', 'site', 'mail', 'txt', 'caa', 'dmarc', 'has_spf']
            results_writer = csv.DictWriter(results_files, fieldnames)
            results_writer.writeheader()

            for line in csv_reader:
                site = line['site']
                mail = safe_query(site, 'mx')
                txt = safe_query(site, 'txt')
                caa = safe_query(site, 'caa')
                dmarc = safe_query('_dmarc.' + site, 'txt')
                is_spf = has_spf(txt)
                results_writer.writerow({'rank': line['rank'], 'site': site, 'mail': mail, 'txt': txt,
                                         'caa': caa, 'dmarc': dmarc, 'has_spf': is_spf})
                sleep(2)
                break


def safe_query(site: str, type: str):
    r = None
    try:
        r = dns.resolver.query(site, type)
    except dns.resolver.NoAnswer:
        pass
    except dns.resolver.NXDOMAIN:
        pass
    if r:
        results = list()
        for ans in r:
            results.append(ans.to_text())
        return results
    else:
        return None


def has_spf(ans):
    for r in ans:
        if r.startswith('"v=spf'):
            return True
    return False


def spf_final_qualifier(record: str):
    pattern = re.compile(r"/[+?~-]all/")
    q = pattern.match(record)
    return q


if __name__ == '__main__':
    get_dns()
