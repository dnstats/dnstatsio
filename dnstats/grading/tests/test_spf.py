import unittest

from dnstats.grading import Grade
from dnstats.grading.spf import grade as grade_spf


class TestSpf(unittest.TestCase):
    def test_invalid(self):
        grade = grade_spf(['not spf',], 'example.com')
        self.assertEqual(0, grade)

    def test_reject_all(self):
        grade = grade_spf(['v=spf1 -all',], 'example.com')
        self.assertEqual(100, grade)

    def test_pass_all(self):
        grade = grade_spf(['v=spf1 +all',], 'example.com')
        self.assertEqual(0, grade)

    def test_pass_an_ipv4_reject_all(self):
        grade = grade_spf(['v=spf1 ip4:1.0.0.0/32 -all',], 'example.com')
        self.assertEqual(100, grade)

    def test_pass_an_ipv4_reject_all_ptr(self):
        grade = grade_spf(['v=spf1 ptr ip4:1.0.0.0/32 -all',], 'example.com')
        self.assertEqual(98, grade)

    def test_default_pass_with_ipv4(self):
        grade = grade_spf(['v=spf1 ip4:1.0.0.0/24',], 'example.com')
        self.assertEqual(20, grade)

    def test_default_pass_with_ipv4_ptr(self):
        grade = grade_spf(['v=spf1 ptr ip4:1.0.0.0/32',], 'example.com')
        self.assertEqual(18, grade)

    def test_a_with_pass_all(self):
        grade = grade_spf(['v=spf1 ptr ip4:1.0.0.0/24 +all',], 'example.com')
        self.assertEqual(0, grade)

    def test_fastmail(self):
        grade = grade_spf(['v=spf1 include:spf.messagingengine.com -all',], 'dnstats.io')
        self.assertEqual(100, grade)

    def test_many_spf_records(self):
        grade = grade_spf(['v=spf1 -all', 'v=spf1 -all'], 'example.com')
        self.assertEqual(0, grade)

