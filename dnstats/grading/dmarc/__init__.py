from enum import Enum

from dnstats.grading import Grade, half_reduce, update_count_dict, half_raise
from dnstats.dnsvalidate.dmarc import validate



def grade(dmarcs: list, domain: str) -> int:
    validate(dmarcs, domain)

