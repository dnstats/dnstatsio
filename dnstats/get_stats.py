from time import sleep
import csv
from dnstats.dnsutils import safe_query, spf_final_qualifier, has_spf


def get_dns():
    with open('dnstats/sites_rank2.csv', 'r') as sites_file:

        with open('dnstats/dns_results.csv', 'w') as results_files:
            csv_reader = csv.DictReader(sites_file)
            fieldnames = ['rank', 'site', 'mail', 'txt', 'caa', 'dmarc', 'has_spf', 'spf_qualifier', 'has_dnssec']
            results_writer = csv.DictWriter(results_files, fieldnames)
            results_writer.writeheader()

            for line in csv_reader:
                site = line['site']
                caa, dmarc, is_spf, mail, spf_qualifier, txt, has_dnsec = get_stats(site)
                results_writer.writerow({'rank': line['rank'], 'site': site, 'mail': mail, 'txt': txt,
                                         'caa': caa, 'dmarc': dmarc, 'has_spf': is_spf, 'spf_qualifier': spf_qualifier,
                                         'has_dnssec': has_dnsec})
                sleep(2)
                break


def get_stats(site):
    mail = safe_query(site, 'mx')
    txt = safe_query(site, 'txt')
    caa = safe_query(site, 'caa')
    dmarc = safe_query('_dmarc.' + site, 'txt')
    is_spf, spf_record = has_spf(txt)
    spf_qualifier = ""
    ds = safe_query(site, 'ds')
    has_dnssec = ds != ""
    if is_spf:
        spf_qualifier = spf_final_qualifier(spf_record)
    return caa, dmarc, is_spf, mail, spf_qualifier, txt, has_dnssec

if __name__ == '__main__':
    get_stats('assignitapp.com')
