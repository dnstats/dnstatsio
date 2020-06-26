import requests


def has_security_txt(domain: str):
    pass
    try:
        r = requests.get('https://{domain}/.well-known/security.txt'.format(domain=domain))
        if r.status_code == 200 and 'text/plain' in r.headers.get('Content-Type'):
            return True
    except Exception:
        pass
    return False

