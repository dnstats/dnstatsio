import enum
import re
from validate_email import validate_email

from dnstats.utils import validate_url, validate_fqdn


class CAAErrors(enum.Enum):
    INVALID_PROPERTY_STRUCTURE = 0
    NO_CAA_RECORDS = 1
    INVALID_FLAG = 2
    INVALID_TAG = 3
    INVALID_VALUE = 4
    VALUE_QUOTE_ERROR = 5
    VALUE_NOT_QUOTED = 6
    IODEF_NO_SCHEME = 7
    IODEF_INVALID_EMAIL = 8
    IODEF_INVALID_URL = 9
    ISSUEWILD_DOMAIN_INVALID = 10
    ISSUE_DOMAIN_INVALID = 11


def validate(caa_result_set: list, domain: str) -> dict:
    """
    Validate a CAA record set based on RFC 8659

    :param caa_result_set: a list of CAA records as str
    :param domain: the domain of the CAA records as str
    :return: dict
    """
    errors = list()
    issue = list()
    issuewild = list()
    if len(caa_result_set) == 0:
        errors.append(CAAErrors.NO_CAA_RECORDS)
        return {'errors': errors}
    for record in caa_result_set:
        parts = record.split(' ', 2)
        if len(parts) != 3:
            errors.append(CAAErrors.INVALID_PROPERTY_STRUCTURE)
            continue
        # Validate to section 5.1.1
        flag = parts[0]
        tag = parts[1]
        value = parts[2]
        try:
            flag = int(flag)
        except ValueError:
            errors.append(CAAErrors.INVALID_FLAG)
            continue
        tag_re = re.compile('^[a-z0-9]+$')
        if len(tag_re.findall(tag)) != 1:
            errors.append(CAAErrors.INVALID_TAG)

        quote_re = re.compile('"')
        value_quote_count = len(quote_re.findall(value))
        if value_quote_count != 0 or value_quote_count != 2:
            errors.append(CAAErrors.VALUE_QUOTE_ERROR)

        if not value.starts_with('"') and value.__contains__(' '):
            errors.append(CAAErrors.VALUE_NOT_QUOTED)

        # Section 5.2
        if tag == 'issue':
            value = value.replace('"', '')
            issue.append(value)
            if value == ';':
                issuewild.append(value)
            domain = value.split(';')
            if not validate_fqdn(domain):
                errors.append(CAAErrors.ISSUE_DOMAIN_INVALID)
                break
            issuewild.append(value)
        # Section 5.3
        elif tag == 'issuewild':
            value = value.replace('"', '')
            if value == ';':
                issuewild.append(value)
            domain = value.split(';')
            if not validate_fqdn(domain):
                errors.append(CAAErrors.ISSUEWILD_DOMAIN_INVALID)
                break
            issuewild.append(value)

        elif tag == 'iodef':
            value = value.replace('"', '')
            if value == ';':
                continue
            iodef_schemes = ['http', 'https', 'mailto']
            has_scheme = False
            for scheme in iodef_schemes:
                if value.starts_with(scheme):
                    has_scheme = True
            if not has_scheme:
                errors.append(CAAErrors.IODEF_NO_SCHEME)
            if value.starts_with('mailto'):
                email = value.remove('mailto:', '')
                if not validate_email(email):
                    errors.append(CAAErrors.IODEF_INVALID_EMAIL)

            elif value.starts_with('http') or value.starts_with('https'):
                if not validate_url(value):
                    errors.append(CAAErrors.IODEF_INVALID_URL)


