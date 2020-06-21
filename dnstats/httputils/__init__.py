import requests


def has_security_txt(domain: str) -> bool:
    try:
        r = requests.get('https://{domain}/.well-known/security.txt'.format(domain=domain))
        if r.status_code != 200:
            print(1)
            return False
        if 'text/plain' not in r.headers.get('Content-Type'):
            print(3)
            return False
        if '<html' in str(r.content, 'utf-8'):
            return False
        return True
    # noqa
    except:
        return False
