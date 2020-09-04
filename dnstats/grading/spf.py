from dnstats.dnsvalidate.spf import Spf, SpfError

SPF_POLICY_GRADE = {
    '-all': 100,
    '~all': 60,
    '?all': 25,
    '+all': 0
}


def grade(spfs: list, domain: str) -> int:
    if len(spfs) != 1:
        return 0
    spf_record = Spf(spfs[0], domain)
    errors = spf_record.errors
    current_grade = SPF_POLICY_GRADE.get(spf_record.final_qualifier)
    if type(current_grade) != int:
        current_grade = 20
    print('spf: {}, {}'.format(spf_record.final_qualifier, current_grade))

    for error in errors:
        if error == SpfError.NO_SPF_FOUND or error == SpfError.INVALID_RECORD_START or \
                error == SpfError.REDIRECT_RETURNED_MANY_SPF or error == SpfError.INVALID_REDIRECT_MECHANISM:
            return 0
    if errors:
        current_grade = current_grade - len(errors) * 2
    print(errors)
    return max(current_grade, 0)


