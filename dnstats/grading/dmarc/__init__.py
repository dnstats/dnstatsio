from enum import Enum

from dnstats.grading import Grade, half_reduce, update_count_dict, half_raise


class DmarcErrors(Enum):
    INVALID_DMARC_RECORD = 0
    INVALID_ADKIM_VALUE = 1
    INVALID_ASPF_VALUE = 2
    INVALID_FAILURE_REPORTING_VALUE = 3
    INVALID_POLICY = 4
    INVALID_SUBDOMAIN_POLICY = 5
    MULTIPLE_DMARC_RECORDS = 6

def grade(dmarcs: list, domain: str) -> int:
    current_grade = 0
    sp = 0
    tag_count = dict()
    errors = list()
    if len(dmarcs) > 1:
        errors.append(DmarcErrors.MULTIPLE_DMARC_RECORDS)
        return current_grade, errors
    dmarc = dmarcs[0]
    pct = False
    has_rua = False
    has_ruf = False
    has_policy = False
    if dmarc and dmarc.startswith('v=DMARC1;'):
        parts = dmarc.split(';')
        for part in parts:
            sub_parts = part.split('=')
            if len(sub_parts) != 2:
                continue
            tag = sub_parts[0].strip()
            value = sub_parts[1].strip()
            update_count_dict(tag_count, tag)
            # TODO: verify that parts are using valid chars
            if tag == 'adkim':
                if value == 's':
                    current_grade += 5
                elif value is not 'r':
                    errors.append(DmarcErrors.INVALID_ADKIM_VALUE)
            elif tag == 'aspf':
                if value == 's':
                    current_grade += 5
                elif value is not 'r':
                    errors.append(DmarcErrors.INVALID_ASPF_VALIE)
            elif tag == 'fo':
                if value == '1':
                    current_grade += 4
                elif value == 'd':
                    current_grade += 2
                elif value == 's':
                    current_grade += 2
                elif value != '0':
                    errors.append(DmarcErrors.INVALID_FAILURE_REPORTING_VALUE)
            elif tag == 'p':
                has_policy = True
                if value == 'none':
                    current_grade += 10
                elif value == 'quarantine':
                    current_grade += 30
                    sp = 10
                elif value == 'reject':
                    current_grade += 60
                    sp = 15
                else:
                    current_grade -= 5
                    sp = 0
                    errors.append(DmarcErrors.INVALID_POLICY)

            elif tag == 'pct':
                pct_value = 0
                pct = True
                try:
                    pct_value = int(value)
                except ValueError:
                    pass
                if pct_value == 0:
                    current_grade -= 2
                elif 70 > pct_value <= 90:
                    current_grade += 1
                elif 90 >= pct_value >= 99:
                    current_grade += 3
                elif pct_value == 100:
                    current_grade += 5
                else:
                    current_grade -= 5
            elif tag == 'rf':
                pass
            elif tag == 'ri':
                pass
            elif tag == 'rua':
                if not has_rua:
                    current_grade += 5
                    has_rua = True
            elif tag == 'ruf':
                if not  has_ruf:
                    current_grade += 5
                    has_ruf = True
            elif tag == 'sp':
                if tag == 'none':
                    sp = 0
                elif tag == 'quarantine':
                    sp = 10
                elif tag == 'reject':
                    sp = 15
                else:
                    current_grade -= 2
                    errors.append(DmarcErrors.INVALID_SUBDOMAIN_POLICY)
            elif tag is 'v':
                pass
            else:
                return 0
    else:
        return current_grade

    if not has_policy:
        return 0

    if not pct:
        current_grade += 5

    return current_grade + sp
