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
    TAG_TOO_LONG = 12


class CAA:
    """
    DNS validation for CAA
    """
    def __init__(self, caa_records: list, domain: str):
        self.caa_records = caa_records
        self.domain = domain

    @property
    def iodef(self) -> list:
        return validate(self.caa_records, self.domain)['iodef']

    @property
    def issue(self) -> list:
        return validate(self.caa_records, self.domain)['issue']

    @property
    def issuewild(self) -> list:
        return validate(self.caa_records, self.domain)['issuewild']

    @property
    def errors(self) -> list:
        return validate(self.caa_records, self.domain)['errors']


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
    iodef = list()
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
        if flag > 128:
            errors.append(CAAErrors.INVALID_FLAG)
        tag_re = re.compile('^[a-z0-9]+$')
        if len(tag_re.findall(tag)) != 1:
            errors.append(CAAErrors.INVALID_TAG)
        if len(tag) > 15:
            errors.append(CAAErrors.TAG_TOO_LONG)

        quote_re = re.compile('"')
        value_quote_count = len(quote_re.findall(value))
        if value_quote_count != 0 and value_quote_count != 2:
            errors.append(CAAErrors.VALUE_QUOTE_ERROR)
            continue

        if not value.startswith('"') and value.__contains__(' '):
            errors.append(CAAErrors.VALUE_NOT_QUOTED)
            continue
        # Section 5.2
        if tag == 'issue':
            value = value.replace('"', '')
            issue.append(value)
            if value == ';':
                issuewild.append(value)
            c_domain = value.split(';')
            if not validate_fqdn(c_domain[0]):
                errors.append(CAAErrors.ISSUE_DOMAIN_INVALID)
                continue
            issuewild.append(value)
        # Section 5.3
        elif tag == 'issuewild':
            value = value.replace('"', '')
            if value == ';':
                issuewild.append(value)
            c_domain = value.split(';')
            if not validate_fqdn(c_domain[0]):
                errors.append(CAAErrors.ISSUEWILD_DOMAIN_INVALID)
                continue
            issuewild.append(value)

        elif tag == 'iodef':
            value = value.replace('"', '')
            if value == ';':
                iodef.append(';')
                continue
            iodef_schemes = ['http', 'https', 'mailto']
            has_scheme = False
            for scheme in iodef_schemes:
                if value.startswith(scheme):
                    has_scheme = True
            if not has_scheme:
                errors.append(CAAErrors.IODEF_NO_SCHEME)
                continue
            iodef.append(value)
            if value.startswith('mailto'):
                email = value.replace('mailto:', '')
                if not validate_email(email):
                    errors.append(CAAErrors.IODEF_INVALID_EMAIL)
                    continue

            elif value.startswith('http') or value.startswith('https'):
                if not validate_url(value):
                    errors.append(CAAErrors.IODEF_INVALID_URL)
                    continue

    result = dict()
    result['errors'] = errors
    result['issue'] = issue
    result['issuewild'] = issuewild
    result['iodef'] = iodef
    return result


