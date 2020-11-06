import unittest

from dnstats.grading.ns import grade as Ns


class TestNs(unittest.TestCase):
    def test_none(self):
        ns = Ns([], {}, {}, 'dnstats.io')[0]
        self.assertEqual(ns, 0)

    def test_one(self):
        ns = Ns(['ns1.dnstats.io.'], {'ns1.dnstats.io.': ['1.1.1.1']}, {'ns1.dnstats.io.': 'ns1.dnstats.io.'}, 'dnstats.io')[0]
        self.assertEqual(ns, 80)

    def test_nameservers_mismatch(self):
        ns = Ns(['ns1.dnstats.io.', 'ns2.dnstats.io.'], {'ns1.dnstats.io.': ['1.1.1.1'], 'ns2.dnstats.io.': ['1.1.1.1']},
                {'ns1.dnstats.io.': 'ns1.dnstats.io.', 'ns2.dnstats.io.': 'ns2.dnstats.io.'}, 'dnstats.io')[0]
        self.assertEqual(ns, 80)

    def test_nameservers_private(self):
        ns = Ns(['ns1.dnstats.io.', 'ns2.dnstats.io.'], {'ns1.dnstats.io.': ['10.0.0.1'], 'ns2.dnstats.io.': ['10.0.0.1']},
                {'ns1.dnstats.io.': 'ns1.dnstats.io.', 'ns2.dnstats.io.': 'ns2.dnstats.io.'}, 'dnstats.io')[0]
        self.assertEqual(ns, 60)
