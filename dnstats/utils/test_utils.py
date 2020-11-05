import unittest
import enum

from dnstats.utils import validate_url, validate_fqdn, count_value


class TestEnum(enum.Enum):
    A = 0
    B = 1


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

    def test_null_count(self):
        self.assertEqual(0, count_value('', []))

    def test_value_no_match(self):
        self.assertEqual(0, count_value('', ['taco']))

    def test_value_match(self):
        self.assertEqual(1, count_value('taco', ['taco']))

    def test_value_matches(self):
        self.assertEqual(2, count_value('taco', ['taco', 'taco']))

    def test_no_match_enum(self):
        self.assertEqual(0, count_value('taco', [TestEnum.A]))

    def test_match_enum(self):
        self.assertEqual(1, count_value(TestEnum.A, [TestEnum.A]))

