from enum import Enum

from dnstats.grading import Grade, half_reduce, update_count_dict, half_raise
from dnstats.dnsvalidate.dmarc import Dmarc



def grade(dmarcs: list, domain: str) -> int:
    errors = Dmarc(dmarcs).errors

