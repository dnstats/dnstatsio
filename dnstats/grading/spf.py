from dnstats.dnsvalidate.spf import Spf, SpfError

SPF_POLICY_GRADE = {
    '-all': 100,
    '~all': 60,
}

def grade(spfs: list, domain: str) -> int:
    if len(spfs) != 1:
        return 0
    spf_record = Spf(spfs[0], domain)
    errors = spf_record.errors
    SPF_POLICY_GRADE.get(spf_record.final_qualifier)

    for error in errors:
        if error == SpfError.NO_SPF_FOUND or error == SpfError.INVALID_RECORD_START:
            return 0

    return 0


