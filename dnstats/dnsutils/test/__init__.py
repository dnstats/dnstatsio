import unittest

from dnstats.dnsutils import validate_label


class TestDnsUtils(unittest.TestCase):
    def test_valid_label(self):
        self.assertTrue(validate_label('taco'))
        self.assertTrue(validate_label('taco4'))
        self.assertTrue(validate_label('taco-4'))
        self.assertTrue(validate_label('t'))
        self.assertTrue(validate_label('tco'))
        self.assertTrue(validate_label('tc'))

    def test_invalid_label(self):
        self.assertFalse(validate_label('4taco'))
        self.assertFalse(validate_label('4taco-'))
