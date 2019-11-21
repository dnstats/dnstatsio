import publicsuffix2
import csv


def parse():
    sites = set()
    with open('data.csv', 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            sites.add((publicsuffix2.get_sld((row['IDN_Domain'])), row['GlobalRank']))

    with open('sites_rank.csv', 'w') as csv_file:
        fieldnames = ['site', 'rank']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        writer.writeheader()

        for site in sites:
            writer.writerow({'site': site[0], 'rank': site[1]})


if __name__ == '__main__':
    parse()