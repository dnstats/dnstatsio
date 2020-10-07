from dnstats.dnsvalidate.spf import Spf, SpfError, extract_spf_from_txt

SPF_POLICY_GRADE = {
    '-all': 100,
    '~all': 60,
    '?all': 35,
    '+all': 0
}


def grade(spfs: list, domain: str, has_mx: True) -> int:
    """
    Grade a given SPF for a given domain.
    :param spfs: a list of txt records for the apex
    :param domain: domain of the given SPF record
    :param has_mx Does the domain have mx records
    :return: A grade for the given input
    """
    spf_txt_record, errors = extract_spf_from_txt(spfs, domain)
    # Return a grade 5 if there is no SPF
    # Since NO SPF is better than pass all
    if has_mx:
        no_spf_grade = 10
    else:
        no_spf_grade = 6

    if len(errors) != 0:
        return no_spf_grade
    if len(spfs) != 1:
        return no_spf_grade
    spf_record = Spf(spf_txt_record, domain)
    errors.extend(spf_record.errors)
    current_grade = SPF_POLICY_GRADE.get(spf_record.final_qualifier)
    if type(current_grade) != int:
        current_grade = 20

    for error in errors:
        if error == SpfError.NO_SPF_FOUND or error == SpfError.INVALID_RECORD_START or \
                error == SpfError.REDIRECT_RETURNED_MANY_SPF or error == SpfError.INVALID_REDIRECT_MECHANISM:
            return no_spf_grade
    if errors:
        current_grade = current_grade - len(errors) * 2

    return max(current_grade, 0)
