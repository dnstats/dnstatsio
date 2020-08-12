import unittest

from dnstats.dnsvalidate.spf import Spf, SpfError


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

    def test_valid_ipv4(self):
        spf_record = Spf("v=spf1 ip4:1.0.0.1/32 -all", 'example.com')
        results = spf_record.is_valid
        print(spf_record.errors)
        self.assertEqual(True, results)

    def test_valid_ipv6(self):
        spf_record = Spf("v=spf1 ip6:2607:f8b0:4009:816::200e/128 -all", 'example.com')
        results = spf_record.is_valid
        print(spf_record.errors)
        self.assertEqual(True, results)

    def test_local_ipv4(self):
        spf_record = Spf("v=spf1 ip4:192.168.0.1/32 -all", 'example.com')
        results = spf_record.is_valid
        errors = spf_record.errors
        self.assertTrue(errors.__contains__(SpfError.INVALID_IPV4_MECHANISM))
        self.assertFalse(errors.__contains__(SpfError.INVALID_IPV4_CIDR))
        self.assertEqual(False, results)

    def test_invalid_cidr_ipv4(self):
        spf_record = Spf("v=spf1 ip4:192.168.0.1/35 -all", 'example.com')
        results = spf_record.is_valid
        errors = spf_record.errors
        errors.__contains__(SpfError.INVALID_IPV4_CIDR)
        print(spf_record.errors)
        self.assertEqual(False, results)

    def test_partial_ipv4(self):
        spf_record = Spf("v=spf1 ip4 -all", 'example.com')
        results = spf_record.is_valid
        errors = spf_record.errors
        self.assertTrue(errors.__contains__(SpfError.INVALID_IPV4_MECHANISM))
        print(spf_record.errors)
        self.assertEqual(False, results)

    def test_partial_ipv6(self):
        spf_record = Spf("v=spf1 ip6 -all", 'example.com')
        results = spf_record.is_valid
        errors = spf_record.errors
        self.assertTrue(errors.__contains__(SpfError.INVALID_IPV6_MECHANISM))
        print(spf_record.errors)
        self.assertEqual(False, results)

    def test_invalid_cidr_ip6(self):
        spf_record = Spf("v=spf1 ip6:2607:f8b0:4009:816::200e/129 -all", 'example.com')
        results = spf_record.is_valid
        errors = spf_record.errors
        self.assertTrue(errors.__contains__(SpfError.INVALID_IPV6_CIDR))
        print(spf_record.errors)
        self.assertEqual(False, results)

    def test_partial_redirect(self):
        spf_record = Spf("v=spf1 redirect -all", 'example.com')
        results = spf_record.is_valid
        errors = spf_record.errors
        self.assertTrue(errors.__contains__(SpfError.INVALID_REDIRECT_MECHANISM))
        print(spf_record.errors)
        self.assertEqual(False, results)

    def test_no_policy(self):
        spf_record = Spf("v=spf1 ", 'example.com')
        results = spf_record.is_valid
        errors = spf_record.errors
        print(spf_record.errors)
        self.assertEqual(True, results)
