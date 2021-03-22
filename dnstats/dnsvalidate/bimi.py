import enum

from dnstats.dnsvalidate.dmarc import Dmarc
from dnstats.utils.abnf import parse_abnf
from dnstats.grading import update_count_dict

class BimiErrors(enum.Enum):
    N0_BIMI_RECORDS = 0
    TOO_MANY_BIMI_RECORDS = 1
    DMARC_STRICT_ENOUGH_POLICY = 2
    DMARC_STRICT_ENOUGH_PERCENT = 3
    INVALID_START = 4
    LOGO_NOT_DEFINED = 5
    LOGO_NOT_HTTPS = 6
    LOGO_INVALID_LOCATION = 7
    LOGO_INVALID_FORMAT = 8
    SELECTOR_NOT_DEFINED = 9
    DUPLICATE_TAG_FOUND = 10
    BIMI_OPTED_OUT = 11
    LOGO_LOCATION_BLANK = 12
    DMARC_NOT_DEFINED = 13

class Bimi:
    """
    Based on https://datatracker.ietf.org/doc/html/draft-blank-ietf-bimi-02
    """
    def __init__(self, records: list, dmarc_records: list):
        self.dmarc_records = dmarc_records
        self._validate(records,)

    def _validate(self, records: list) -> dict:
        result = {}
        self.errors = []
        if not records or len(records) <= 0:
            self.errors.append(BimiErrors.N0_BIMI_RECORDS)
            return result

        if len(records) > 1:
            self.errors.append(BimiErrors.TOO_MANY_BIMI_RECORDS)
            return result

        if len(self.dmarc_records) < 1:
            self.errors.append(BimiErrors.DMARC_NOT_DEFINED)

        dmarc = Dmarc(self.dmarc_records)

        if dmarc.p not in ['reject', 'quarantine']:
            self.errors.append(BimiErrors.DMARC_STRICT_ENOUGH_POLICY)
            return result

        if dmarc.p == 'quarantine' and str(dmarc.pct) != '100':
            self.errors.append(BimiErrors.DMARC_STRICT_ENOUGH_PERCENT)
            return result

        bimi_record = records[0]

        if not bimi_record.startswith('v=BIMI1'):
            self.errors.append(BimiErrors.INVALID_START)
            return result


        parsed, dups = parse_abnf(bimi_record)

        if dups:
            self.errors.append(BimiErrors.DUPLICATE_TAG_FOUND)


        if 'l' not in parsed:
            self.errors.append(BimiErrors.LOGO_NOT_DEFINED)
            self.l = None
        else:
            if parsed['l'].startswith('http://'):
                self.errors.append(BimiErrors.LOGO_NOT_HTTPS)
                return result

            if not parsed['l'].startswith('https://') and not parsed['l'] == '':
                self.errors.append(BimiErrors.LOGO_INVALID_LOCATION)
                return result

            if not parsed['l'].endswith('.svg') and not parsed['l'].endswith('.svgz') and not parsed['l'] == '':
                self.errors.append(BimiErrors.LOGO_INVALID_FORMAT)

            self.l = parsed['l']


        if not self.__validate_selctor(parsed, result):
            return result

        if self.selector and self.l == '':
            self.errors.append(BimiErrors.LOGO_LOCATION_BLANK)



    def __validate_selctor(self, parsed, result) -> bool:
        if 's' not in parsed:
            self.errors.append(BimiErrors.SELECTOR_NOT_DEFINED)
            self.selector = None
            return False
        if parsed.get('s') == '' and self.l == '':
            self.opt_out = True
            self.errors.append(BimiErrors.BIMI_OPTED_OUT)
            self.selector = ''
            return True
        else:
            self.opt_out = False
            self.selector = parsed['s']
            return True
