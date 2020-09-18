import unittest
from dnstats.utils import validate_url, validate_fqdn


class TestUtils(unittest.TestCase):
    def test_valid_url(self):
        self.assertTrue(validate_url('https://dnstats.io'))

    def test_invalid_url_bad_scheme(self):
        self.assertFalse(validate_url('taco://dnstats.io'))

    def test_invalid_url_no_scheme(self):
        self.assertFalse(validate_url('dnstats.io'))

    def test_valid_fqdn(self):
        self.assertTrue(validate_fqdn('dnstats.io'))

    def test_invalid_fqdn_name(self):
        self.assertFalse(validate_fqdn('dnstats'))

    def test_invalid_fqdn_scheme(self):
        self.assertFalse(validate_fqdn('https://dnstats.io'))
