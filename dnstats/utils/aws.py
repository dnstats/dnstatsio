import datetime
from hashlib import sha1
import hmac
import requests
import binascii


from dnstats import settings


def s3_upload_string(bucket: str, filename: str, data: str):
    resource = f'/{bucket}/{filename}'
    content_type = _get_mime_type_from_filename(filename)
    date_value = datetime.datetime.now().astimezone().strftime('%a, %d %b %Y %H:%M:%S %z')
    signed_data = _sign_string(f'PUT\n\n{content_type}\n{date_value}\n{resource}')
    hostname = _get_base_url()
    headers = _build_headers(content_type, signed_data)
    requests.put(f'{hostname}{bucket}/{filename}', headers=headers, data=data)


def _build_headers(content_type, signed_data):
    headers = dict()
    headers['Host'] = _get_hostname()
    headers['Content-Type'] = content_type
    headers['Date'] = datetime.datetime.now().astimezone().strftime('%a, %d %b %Y %H:%M:%S %z')
    headers['Authorization'] = f'AWS {settings.REPORT_S3_ACCESS_KEY}:{signed_data}'
    return headers


def _get_mime_type_from_filename(filename: str) -> str:
    if filename.endswith('.json'):
        return 'application/json'
    if filename.endswith('.csv'):
        return 'text/csv'
    return 'text/plain'


def _sign_string(data: str) -> str:
    hmaced_signed = hmac.new(bytes(settings.REPORT_S3_SECRET_KEY, 'utf-8'), bytes(data, 'utf-8'), sha1)
    return str(binascii.b2a_base64(hmaced_signed.digest()), 'utf-8').replace('\n', '')


def _get_base_url() -> str:
    result = ''
    if not settings.REPORT_S3_URL_BASE:
        raise ValueError('REPORT_S3_URL_BASE is not defined')

    if settings.REPORT_S3_URL_BASE.startswith('http://'):
        raise ValueError('Cowardly refusing to upload without TLS.')

    if not settings.REPORT_S3_URL_BASE.startswith('https://'):
        result += 'https://'
    result += settings.REPORT_S3_URL_BASE
    if not settings.REPORT_S3_URL_BASE.endswith('/'):
        result += '/'
    return result


def _get_hostname():
    if not settings.REPORT_S3_URL_BASE:
        raise ValueError('REPORT_S3_URL_BASE is not defined')
    return settings.REPORT_S3_URL_BASE.replace('https:', '').replace('/', '')
