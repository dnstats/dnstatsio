import unittest
from dnstats.dnsvalidate.ns import Ns, NsErrors


class TestNs(unittest.TestCase):
    def test_none(self):
        ns = Ns([], {}, {}, 'dnstats.io')
        self.assertTrue(ns.errors.__contains__(NsErrors.NO_NS_RECORDS))

    def test_one(self):
        ns = Ns(['ns1.dnstats.io.'], {'ns1.dnstats.io.': ['1.1.1.1']}, {'ns1.dnstats.io.': 'ns1.dnstats.io.'},
                'dnstats.io')
        self.assertFalse(ns.errors.__contains__(NsErrors.NO_NS_RECORDS))

    def test_nameservers_mismatch(self):
        ns = Ns(['ns1.dnstats.io.', 'ns2.dnstats.io.'], {'ns1.dnstats.io.': ['1.1.1.1'], 'ns2.dnstats.io.': ['1.1.1.1']},
                {'ns1.dnstats.io.': 'ns1.dnstats.io.', 'ns2.dnstats.io.': 'ns2.dnstats.io.'}, 'dnstats.io')
        self.assertFalse(ns.errors.__contains__(NsErrors.NO_NS_RECORDS))
        self.assertTrue(ns.errors.__contains__(NsErrors.NAME_SERVER_MISMATCH))

    def test_nameservers_private(self):
        ns = Ns(['ns1.dnstats.io.', 'ns2.dnstats.io.'], {'ns1.dnstats.io.': ['10.0.0.1'], 'ns2.dnstats.io.': ['10.0.0.1']},
                {'ns1.dnstats.io.': 'ns1.dnstats.io.', 'ns2.dnstats.io.': 'ns2.dnstats.io.'}, 'dnstats.io')
        self.assertFalse(ns.errors.__contains__(NsErrors.NO_NS_RECORDS))
        self.assertTrue(ns.errors.__contains__(NsErrors.NAMESERVER_IS_NOT_PUBLIC))

