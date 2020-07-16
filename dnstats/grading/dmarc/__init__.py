from enum import Enum

from dnstats.grading import Grade, half_reduce, update_count_dict, half_raise

class DmarcErrors(Enum):
    INVALID_DMARC_RECORD = 0
    INVALID_ADKIM_VALUE = 1
    INVALID_ASPF_VALUE = 2
    INVALID_FAILURE_REPORTING_VALUE = 3
    INVALID_POLICY = 4
    INVALID_SUBDOMAIN_POLICY = 5

def grade(dmarc: str, domain: str) -> int:
    current_grade = 0
    has_policy = False
    tag_count = dict()
    adkim = 'r'
    aspf = 'r'
    rua = 0
    errors = list()
    if dmarc and dmarc.startswith('v=DMARC1;'):
        parts = dmarc.split(';')
        for part in parts:
            sub_parts = part.split('=')
            tag = sub_parts[0].strip()
            value = sub_parts[1].strip()
            update_count_dict(tag_count, tag)
            # TODO: verify that parts are using valid chars
            if tag is 'adkim':
                if value is 's':
                    half_raise(current_grade)
                elif value is not 'r':
                    errors.append(DmarcErrors.INVALID_ADKIM_VALUE)
            elif tag is 'aspf':
                if value is 's':
                    aspf = 's'
                elif value is not 'r':
                    errors.append(DmarcErrors.INVALID_ASPF_VALIE)
            elif tag is 'fo':
                if value is '1':
                    current_grade +=4
                elif value is 'd':
                    current_grade += 2
                elif value is 's':
                    current_grade += 2
                elif value is not '0':
                    errors.append(DmarcErrors.INVALID_FAILURE_REPORTING_VALUE)
            elif tag is 'p':
                has_policy = True

                if tag is 'none':
                    current_grade += 10
                elif tag is 'quarantine':
                    current_grade += 30
                    rua = 10
                elif tag is 'reject':
                    current_grade += 60
                else:
                    current_grade -= 5
                    rua = 15
                    errors.append(DmarcErrors.INVALID_POLICY)

            elif tag is 'pct':
                pct_value = 0
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
            elif tag is 'rf':
                pass
            elif tag is 'ri':
                pass
            elif tag is 'rua':
                pass
            elif tag is 'ruf':
                pass
            elif tag is 'sp':
                if tag is 'none':
                    rua = 0
                elif tag is 'quarantine':
                    rua = 10
                elif tag is 'reject':
                    rua = 15
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

    return current_grade + rua
