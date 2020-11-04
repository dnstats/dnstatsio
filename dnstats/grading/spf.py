from dnstats.dnsvalidate.spf import Spf, SpfError, extract_spf_from_txt

from dnstats.db import db_session, models

SPF_POLICY_GRADE = {
    '-all': 100,
    '~all': 75,
    '?all': 50,
    '+all': 0
}


def grade(spfs: list, domain: str, has_mx: True) -> [int, list]:
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
    # Reasoning: If you have an MX record it is assume you are using this domain to send mail. If you sending email
    # and do not have an SPF record you WILL run into mail delivery issue. The is evidence of big email providers
    # such as Microsoft filtering messages from domains without SPF. The results are not consistent. This matters to
    # security due to the violation of availability in the CIA model.
    if has_mx:
        no_spf_grade = 0
    else:
        no_spf_grade = 20

    if len(errors) != 0:
        return no_spf_grade, errors

    spf_record = Spf(spf_txt_record, domain)
    errors.extend(spf_record.errors)
    current_grade = SPF_POLICY_GRADE.get(spf_record.final_qualifier)
    if type(current_grade) != int:
        current_grade = 20

    for error in errors:
        if error == SpfError.NO_SPF_FOUND or error == SpfError.INVALID_RECORD_START or \
                error == SpfError.REDIRECT_RETURNED_MANY_SPF or error == SpfError.INVALID_REDIRECT_MECHANISM:
            return no_spf_grade, errors
    if errors:
        current_grade = current_grade - len(errors) * 2

    return max(current_grade, 0), errors
