import unittest

from dnstats.grading import Grade
from dnstats.grading.spf import grade as grade_spf


class TestSpf(unittest.TestCase):
    def test_invalid(self):
        grade = grade_spf(['not spf'], 'example.com', False)
        self.assertEqual(20, grade)

    def test_invalid_with_mx(self):
        grade = grade_spf(['not spf'], 'example.com', True)
        self.assertEqual(0, grade)

    def test_no_spf_no_mx(self):
        grade = grade_spf([], 'example.com', False)
        self.assertEqual(20, grade)

    def test_no_spf_with_mx(self):
        grade = grade_spf([], 'example.com', True)
        self.assertEqual(0, grade)

    def test_reject_all(self):
        grade = grade_spf(['v=spf1 -all'], 'example.com', False)
        self.assertEqual(100, grade)

    def test_pass_all(self):
        grade = grade_spf(['v=spf1 +all'], 'example.com', False)
        self.assertEqual(0, grade)

    def test_pass_an_ipv4_reject_all(self):
        grade = grade_spf(['v=spf1 ip4:1.0.0.0/32 -all'], 'example.com', False)
        self.assertEqual(100, grade)

    def test_pass_an_ipv4_reject_all_ptr(self):
        grade = grade_spf(['v=spf1 ptr ip4:1.0.0.0/32 -all'], 'example.com', False)
        self.assertEqual(98, grade)

    def test_default_pass_with_ipv4(self):
        grade = grade_spf(['v=spf1 ip4:1.0.0.0/24'], 'example.com', False)
        self.assertEqual(20, grade)

    def test_default_pass_with_ipv4_ptr(self):
        grade = grade_spf(['v=spf1 ptr ip4:1.0.0.0/32'], 'example.com', False)
        self.assertEqual(18, grade)

    def test_a_with_pass_all(self):
        grade = grade_spf(['v=spf1 ptr ip4:1.0.0.0/24 +all'], 'example.com', False)
        self.assertEqual(0, grade)

    def test_fastmail(self):
        grade = grade_spf(['v=spf1 include:spf.messagingengine.com -all'], 'dnstats.io', False)
        self.assertEqual(100, grade)

    def test_tacos_all(self):
        grade = grade_spf(['v=spf1 include:tacos.all -all'], 'dnstats.io', False)
        self.assertEqual(100, grade)

    def test_tacos_sub_all(self):
        grade = grade_spf(['v=spf1 include:tacos.all ~all'], 'dnstats.io', False)
        self.assertEqual(75, grade)

    def test_tacos_all_default(self):
        grade = grade_spf(['v=spf1 include:tacos.all'], 'dnstats.io', False)
        self.assertEqual(20, grade)

    def test_many_spf_records(self):
        grade = grade_spf(['"v=spf1 -all"', '"v=spf1 -all"'], 'example.com', False)
        self.assertEqual(20, grade)
