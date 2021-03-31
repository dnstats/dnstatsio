from dnstats.grading import update_count_dict

def parse_abnf(record: list) -> [dict, bool]:
    result = dict()
    dups = False
    parts = record.split(';')
    for part in parts:
        sub_parts = part.split('=')
        if len(sub_parts) != 2:
            continue
        tag = sub_parts[0].strip()
        value = sub_parts[1].strip()
        if result.get(tag):
            dups = True
        result[tag] = value

    return result, dups