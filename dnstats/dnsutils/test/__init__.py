import unittest

from dnstats.dnsutils import validate_label, validate_domain


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
        self.assertFalse(validate_label('com-'))

    def test_valid_domain(self):
        self.assertTrue(validate_domain('taco'))
        self.assertTrue(validate_domain('taco.com'))
        self.assertTrue(validate_domain('sub.taco.com'))
        self.assertTrue(validate_domain('long.sub.taco.com'))
        self.assertTrue(validate_domain('taco4.com'))
        self.assertTrue(validate_domain('mab879.com'))
        self.assertTrue(validate_domain('mab879.com.'))

    def test_invalid_domain(self):
        self.assertFalse(validate_domain('4taco.com'))
        self.assertFalse(validate_domain('4-taco.com'))
        self.assertFalse(validate_domain('taco.com-'))
       
