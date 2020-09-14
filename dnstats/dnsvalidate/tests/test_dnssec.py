import unittest

from dnstats.dnsvalidate.dnssec import DnsSec, DnsSecErrors


class TestDnsSec(unittest.TestCase):
    def no_ds(self):
        dnssec = DnsSec([], 'examlpe.com')
        self.assertEqual([DnsSecErrors.NO_DS_RECORDS], dnssec.errors)
