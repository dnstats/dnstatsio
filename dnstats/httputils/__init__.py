import requests


def has_security_txt(domain: str, logger):
    pass
    try:
        logger.debug('started has security.txt for {}'.format(domain))
        r = requests.get('https://{domain}/.well-known/security.txt'.format(domain=domain))
        if r.status_code == 200 and 'text/plain' in r.headers.get('Content-Type'):
            return True
    except Exception:
        logger.debug('error security.txt for {}'.format(domain))
        pass
    return False

