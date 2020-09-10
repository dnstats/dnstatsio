import unittest

from dnstats.dnsvalidate.caa import validate as validate_caa


class TestCaa(unittest.TestCase):
    def test_something(self):
        grade = validate_caa(list(), 'example.com')
        self.assertEqual(0, grade)
