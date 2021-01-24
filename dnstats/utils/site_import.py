import io
import zipfile
import requests
from dnstats.utils.email import _send_sites_updated_started


def setup_import_list(logger):
    _send_sites_updated_started()
    logger.warning("Downloading site list")
    url = "https://tranco-list.eu/top-1m.csv.zip"
    r = requests.get(url)
    csv_content = zipfile.ZipFile(io.BytesIO(r.content)).read('top-1m.csv').splitlines()
    new_sites = dict()
    for row in csv_content:
        row = row.split(b',')
        new_sites[str(row[1], 'utf-8')] = int(row[0])
    return new_sites


def run_rank_site(existing_sites, new_sites):
    unranked_sites = existing_sites.keys() - new_sites.keys()
    for site in unranked_sites:
        _unrank_domain.s(str(site)).apply_async()
        logger.debug("Unranking site: {}".format(site))