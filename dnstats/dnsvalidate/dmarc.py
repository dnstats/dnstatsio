from enum import Enum

from dnstats.grading import update_count_dict


class DmarcErrors(Enum):
    INVALID_DMARC_RECORD = 0
    INVALID_ADKIM_VALUE = 1
    INVALID_ASPF_VALUE = 2
    INVALID_FAILURE_REPORTING_VALUE = 3
    INVALID_POLICY = 4
    INVALID_SUBDOMAIN_POLICY = 5
    MULTIPLE_DMARC_RECORDS = 6
    INVALID_RF_VALUE = 7
    INVALID_RI_VALUE = 8
    INVALID_PCT_VALUE = 9
    INVALID_DMARC_RECORD_START = 10


class Dmarc:
    def __init__(self, dmarc_result_set):
        self.dmarc_result_set = dmarc_result_set

    @property
    def is_valid(self) -> bool:
        return len(validate(self.dmarc_result_set)['errors']) == 0

    @property
    def errors(self) -> list:
        return validate(self.dmarc_result_set)['errors']


def validate(dmarc_result_set: list) -> dict:
    dmarc_record_values = dict()
    tag_count = dict()
    errors = list()
    if len(dmarc_result_set) > 1:
        errors.append(DmarcErrors.MULTIPLE_DMARC_RECORDS)
        dmarc_record_values['errors'] = errors
        return dmarc_record_values
    dmarc_record = dmarc_result_set[0]
    has_rua = False
    has_ruf = False
    if dmarc_record and dmarc_record.startswith('v=DMARC1;'):
        parts = dmarc_record.split(';')
        for part in parts:
            sub_parts = part.split('=')
            if len(sub_parts) != 2:
                continue
            tag = sub_parts[0].strip()
            value = sub_parts[1].strip()
            update_count_dict(tag_count, tag)
            # TODO: verify that parts are using valid chars
            if tag == 'adkim':
                dmarc_record_values['adkim'] = value
                if value not in ['s', 'r']:
                    errors.append(DmarcErrors.INVALID_ADKIM_VALUE)
            elif tag == 'aspf':
                dmarc_record_values['aspf'] = value
                if value not in ['s', 'r']:
                    errors.append(DmarcErrors.INVALID_ASPF_VALIE)
            elif tag == 'fo':
                dmarc_record_values['fo'] = value
                if value not in ['1', 'd', 's', '0']:
                    errors.append(DmarcErrors.INVALID_FAILURE_REPORTING_VALUE)
            elif tag == 'p':
                dmarc_record_values['p'] = value
                if value not in ['none', 'quarantine', 'reject']:
                    errors.append(DmarcErrors.INVALID_POLICY)
            elif tag == 'pct':
                pct_value = 100
                try:
                    pct_value = int(value)
                except ValueError:
                    pass
                if 0 < pct_value < 100:
                    errors.append(DmarcErrors.INVALID_PCT_VALUE)
                dmarc_record_values['pct'] = pct_value
            elif tag == 'rf':
                dmarc_record_values['rf'] = value
                values = value.split(';')
                for rf in values:
                    if rf != 'afrf':
                        errors.append(DmarcErrors.INVALID_RF_VALUE)
            elif tag == 'ri':
                try:
                    ri = int(value)
                except ValueError:
                    errors.append(DmarcErrors.INVALID_RI_VALUE)
                    continue
                if ri < 0 or ri > 4294967295:
                    errors.append(DmarcErrors.INVALID_RI_VALUE)

                dmarc_record_values['ri'] = ri

            elif tag == 'rua':
                dmarc_record_values['rua'] = value
                if not has_rua:
                    has_rua = True
            elif tag == 'ruf':
                dmarc_record_values['ruf'] = value
                if not has_ruf:
                    has_ruf = True
            elif tag == 'sp':
                dmarc_record_values['sp'] = value
                if value not in ['none', 'quarantine', 'reject']:
                    errors.append(DmarcErrors.INVALID_SUBDOMAIN_POLICY)
            elif tag is 'v':
                dmarc_record_values['v'] = value
            else:
                dmarc_record_values[tag] = value
    else:
        errors.append(DmarcErrors.INVALID_DMARC_RECORD_START)
        dmarc_record_values['errors'] = errors
        return dmarc_record_values

    dmarc_record_values['errors'] = errors
    return dmarc_record_values
