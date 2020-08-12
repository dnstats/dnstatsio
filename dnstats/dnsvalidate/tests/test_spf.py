import unittest

from dnstats.dnsvalidate.spf import Spf


class TestSpf(unittest.TestCase):
    def test_valid_reject_all(self):
        spf_record = Spf("v=spf1 -all", 'example.com')
        results = spf_record.is_valid
        print(spf_record.errors)
        self.assertEqual(True, results)

    def test_invalid_nonsense(self):
        spf_record = Spf("taco", 'example.com')
        results = spf_record.is_valid
        print(spf_record.errors)
        self.assertEqual(False, results)
