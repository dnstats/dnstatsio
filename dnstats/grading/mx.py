from dnstats.dnsvalidate.mx import Mx, MXErrors


def grade(mxs: list, domain: str) -> [int, list]:
    mx = Mx(mxs)

    if MXErrors.NO_MX_RECORDS in mx.errors or len(mx.valid_mx_records) == 0:
        return 0, mx.errors

    invalid_size = len(mxs) - len(mx.valid_mx_records)
    final_grade = 100

    if invalid_size > 0 and len(mxs) > 0:
        percentage = len(mx.valid_mx_records) / len(mxs)
        final_grade *= percentage

    for error in mx.errors:
        if error == MXErrors.POSSIBLE_BAD_EXCHANGE:
            final_grade -= 5

    return final_grade, mx.errors
