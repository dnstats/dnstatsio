import ipaddress
from dnstats.dnsutils.spf import get_spf_stats, spf_final_qualifier
from dnstats.dnsutils import safe_query
from enum import Enum


class SpfError(Enum):
    NONE = 0
    INVALID_RECORD_START = 1
    HAS_PTR = 2
    TOO_MANY_DNS_LOOKUPS = 3
    DEFAULT_ALL_QUALIFIER = 4
    INVALID_INCLUDE_FORMAT = 5
    INCLUDE_RETURNED_MANY_SPF = 6
    TOO_MANY_A_RECORDS_RETURNED = 7
    INVALID_A_MECHANISM = 8
    INVALID_MX_MECHANISM = 9
    TOO_MANY_MX_RECORDS_RETURNED = 10
    INVALID_REDIRECT_MECHANISM = 11
    NO_RECORD_AT_REDIRECT = 12
    REDIRECT_RETURNED_MANY_SPF = 13
    INVALID_IPV4_MECHANISM = 14
    INVALID_IPV6_MECHANISM = 15
    INVALID_MECHANISM = 16
    MULTIPLE_SPF_RECORDS = 17
    NO_SPF_FOUND = 18
    INVALID_IPV4_CIDR = 19
    INVALID_IPV6_CIDR = 20
    TOO_MANY_ENDINGS = 21
    TOO_MANY_STARTS = 22
    NO_MX_RECORDS = 23
    NO_A_RECORDS_IN_MECHANISM = 24
    NO_MX_RECORDS_IN_MECHANISM = 25
    INVALID_IPV4_VALUE = 26
    INVALID_IPV6_VALUE = 27


class Spf:
    def __init__(self, spf: str, domain: str):
        self.spf_record = spf
        self.domain = domain

    @property
    def is_valid(self):
        return len(_validate_spf(self.spf_record, self.domain)["errors"]) == 0

    @property
    def errors(self):
        """
        This method checks the SPF returns any errors. See `dnstats.dnsvalidate.spf.SpfErrors` to translate the
        errors into English
        :return: list of `SpfError`
        """
        return _validate_spf(self.spf_record, self.domain)['errors']

    @property
    def final_qualifier(self):
        return spf_final_qualifier(self.spf_record)
    
    @property
    def stats(self):
        return get_spf_stats([self.spf_record])


def extract_spf_from_txt(txt_records: list, domain: str):
    spfs = list()
    errors = list()
    if not txt_records:
        errors.append(SpfError.NO_SPF_FOUND)
        return False, errors

    for record in txt_records:
        record = record.replace('"', '')
        if record.startswith('v=spf1'):
            spfs.append(record)
    if len(spfs) == 1:
        return spfs[0], list()
    elif len(spfs) < 1:
        errors.append(SpfError.NO_SPF_FOUND)
        return False, errors
    else:
        errors.append(SpfError.MULTIPLE_SPF_RECORDS)
        return False, errors


def _validate_spf(spf: str, domain: str) -> {}:
    errors = list()
    if not spf.startswith('v=spf1 '):
        errors.append(SpfError.INVALID_RECORD_START)
    parts = spf.split(' ')
    parts_to_consider = list()
    parts_to_consider.extend(parts)
    count = 1
    inter = 0
    result = dict()
    end_again = False
    start_again = False
    for part in parts_to_consider:
        # Ignore whitespace
        if not part:
            break
        inter += 1
        if count >= 10:
            errors.append(SpfError.TOO_MANY_DNS_LOOKUPS)
            break
    # START Mechanisms as defined in RFC 7208 Sec. 5
        if part.startswith('all'):
            # TODO: check for others and reduce grade if others mechanism are after (RFC 7209 5.1)
            result['errors'] = errors
            return result
        elif part.startswith('include'):
            count += 1
            sub_parts = part.split(':')
            if len(sub_parts) != 2:
                errors.append(SpfError.INVALID_INCLUDE_FORMAT)
                break
        elif part.startswith('a'):
            count += 1
            a_result = safe_query(domain, 'a')
            if not a_result:
                errors.append(SpfError.NO_A_RECORDS_IN_MECHANISM)
                break
            if len(a_result) > 10:
                errors.append(SpfError.TOO_MANY_A_RECORDS_RETURNED)
                break
            # TODO: Process if this mech has :
        elif part.startswith('mx'):
            count += 1
            mx_result = safe_query(domain, 'mx')
            if not mx_result:
                errors.append(SpfError.NO_MX_RECORDS)
                continue
            if not mx_result:
                errors.append(SpfError.NO_MX_RECORDS_IN_MECHANISM)
                break
            if len(mx_result) > 10:
                errors.append(SpfError.TOO_MANY_MX_RECORDS_RETURNED)
                break
            # TODO: Process if this mech has :
        elif part.startswith('ip4'):
            ip = part.split(':', 1)
            try:
                if len(ip) < 2:
                    errors.append(SpfError.INVALID_IPV4_MECHANISM)
                    break
                ip_parts = ip[1].split('/', 1)
                if len(ip_parts) > 1:
                    if not ipaddress.IPv4Network(ip[1]).is_global:
                        errors.append(SpfError.INVALID_IPV4_MECHANISM)
                        break
                else:
                    if not ipaddress.IPv4Network(ip[1], strict=False).is_global:
                        errors.append(SpfError.INVALID_IPV4_MECHANISM)
                        break
            except ipaddress.NetmaskValueError:
                errors.append(SpfError.INVALID_IPV4_CIDR)
            except ipaddress.AddressValueError:
                errors.append(SpfError.INVALID_IPV4_VALUE)
            except:
                errors.append(SpfError.INVALID_IPV6_MECHANISM)

        elif part.startswith('ip6'):
            ip = part.split(':', 1)
            if len(ip) < 2:
                errors.append(SpfError.INVALID_IPV6_MECHANISM)
                break
            ip_parts = ip[1].split('/', 1)
            try:
                if len(ip_parts) > 1:
                    if not ipaddress.IPv6Network(ip[1]).is_global:
                        errors.append(SpfError.INVALID_IPV6_MECHANISM)
                        break
                else:
                    if not ipaddress.IPv6Address(ip[0]).is_global:
                        errors.append(SpfError.INVALID_IPV6_VALUE)
                        break
            except ipaddress.NetmaskValueError:
                errors.append(SpfError.INVALID_IPV6_CIDR)
            except ipaddress.AddressValueError:
                errors.append(SpfError.INVALID_IPV6_VALUE)
            except:
                errors.append(SpfError.INVALID_IPV6_MECHANISM)
        elif part.startswith('ptr'):
            # Count as one DNS query. No way to valid this without an email
            count += 1
            errors.append(SpfError.HAS_PTR)
            # RFC 7208 states "ptr (do not use)"
        elif part.startswith('exists'):
            # We don't need to valid the name exists, as not existing is a valid part of the flow
            count += 1
    # END Mechanisms as defined in RFC 7208 Sec. 5
    # START Modifiers as defined in RFC 7208 Sec. 6
        elif part.startswith('redirect'):
            sub_parts = part.split('=')
            if len(sub_parts) != 2:
                errors.append(SpfError.INVALID_REDIRECT_MECHANISM)
                break
            # TODO: check if valid DNS Name
            if len(sub_parts) == 2:
                redirect_query = safe_query(sub_parts[1], 'txt')
                if redirect_query is None or len(redirect_query) == 0:
                    errors.append(SpfError.INVALID_REDIRECT_MECHANISM)
                    break
                has_spf = False
                for record in redirect_query:
                    record = record.replace('"', '')
                    if record.startswith('v=spf1 '):
                        if not has_spf:
                            for spf_part in record.split(' '):
                                parts_to_consider.append(spf_part)
                            has_spf = True
                if not has_spf:
                    errors.append(SpfError.NO_RECORD_AT_REDIRECT)
            else:
                errors.append(SpfError.INVALID_REDIRECT_MECHANISM)
            count += 1
        elif part.startswith('exp='):
            pass
        elif part.startswith('unknown-modifier='):
            pass
        elif part.endswith('all'):
            if end_again:
                errors.append(SpfError.TOO_MANY_ENDINGS)
            end_again = True
            pass
        elif part.startswith('v='):
            if start_again:
                errors.append(SpfError.TOO_MANY_STARTS)
            sub_parts = part.split('=')
            if sub_parts[1] != 'spf1':
                errors.append(SpfError.INVALID_RECORD_START)
                break
            start_again = True
        else:
            errors.append(SpfError.INVALID_MECHANISM)
            # TODO: account for new modifiers
            break
    # END Modifiers as defined in RFC 7208 Sec. 6

    result['errors'] = errors
    return result
