from enum import Enum

from dnstats.grading import Grade, half_reduce, update_count_dict, half_raise

class DmarcErrors(Enum):
    INVALID_DMARC_RECORD = 0
    INVALID_ADKIM_VALUE = 1
    INVALID_ASPF_VALIE = 2

def grade(dmarc: str, domain: str) -> Grade:
    current_grade = 0
    has_policy = False
    tag_count = dict()
    adkim = 'r'
    aspf = 'r'
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
                pass
            elif tag is 'p':
                has_policy = True
                pass
            elif tag is 'pct':
                pass
            elif tag is 'rf':
                pass
            elif tag is 'ri':
                pass
            elif tag is 'rua':
                pass
            elif tag is 'ruf':
                pass
            elif tag is 'sp':
                pass
            elif tag is 'v':
                pass
            else:
                return Grade.F
    else:
        return current_grade

    if not has_policy:
        return Grade.F
