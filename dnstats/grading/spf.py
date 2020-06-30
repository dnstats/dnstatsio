from grading import Grade

from dnsutils.spf import spf_final_qualifier


def grade(spf: str):
    if spf.startswith('v=spf1 '):
        return Grade.F

    parts = spf.split(' ')
    ptr = parts.__contains__('ptr')
    final = spf_final_qualifier(spf)
