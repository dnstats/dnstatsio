import dns
from time import sleep
import csv


def get_dns():
    with open('dnstats/sites_rank.csv', 'r') as sites_file:

        with open('dnsstats/dns_results.csv', 'w') as results_files:
            csv_reader = csv.DictReader(sites_file)
            fieldnames = ['rank', 'site', 'mail', 'txt', 'caa', 'dmarc']
            results_writer = csv.DictWriter(results_files, fieldnames)
            results_writer.writeheader()

            for line in csv_reader:
                site = line['site']
                mail = safe_query(site, 'mx')
                txt = safe_query(site, 'txt')
                caa = safe_query(site, 'caa')
                dmarc = safe_query('_dmarc.' + site, 'txt')
                results_writer.writerow({'rank': line['rank'], 'site': site, 'mail': mail, 'txt': txt,
                                         'caa': caa, 'dmarc': dmarc})
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



if __name__ == '__main__':
    get_dns()
