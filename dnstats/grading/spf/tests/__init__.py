import unittest

from dnstats.grading import Grade
from dnstats.grading.spf import grade as grade_spf


class TestSpf(unittest.TestCase):
    def test_invalid(self):
        grade = grade_spf(('not spf',), 'example.com')
        self.assertEqual(Grade.F.value, grade[0].value)

    def test_reject_all(self):
        grade = grade_spf(('v=spf1 -all',), 'example.com')
        self.assertEqual(Grade.A.value, grade[0].value)

    def test_pass_all(self):
        grade = grade_spf(('v=spf1 +all',), 'example.com')
        self.assertEqual(Grade.D.value, grade[0].value)

    def test_pass_an_ipv4_reject_all(self):
        grade = grade_spf(('v=spf1 ipv4:10.0.0.1 -all',), 'example.com')
        self.assertEqual(Grade.A.value, grade[0].value)

    def test_pass_an_ipv4_reject_all_ptr(self):
        grade = grade_spf(('v=spf1 ptr ipv4:10.0.0.1 -all',), 'example.com')
        self.assertEqual(Grade.A_MINUS.value, grade[0].value)

    def test_default_pass_with_ipv4(self):
        grade = grade_spf(('v=spf1 ipv4:10.0.0.1',), 'example.com')
        self.assertEqual(Grade.C_MINUS.value, grade[0].value)

    def test_default_pass_with_ipv4_ptr(self):
        grade = grade_spf(('v=spf1 ptr ipv4:10.0.0.1',), 'example.com')
        self.assertEqual(Grade.D_PLUS.value, grade[0].value)

    def test_a_with_pass_all(self):
        grade = grade_spf(('v=spf1 ptr ipv4:10.0.0.1 +all',), 'example.com')
        self.assertEqual(Grade.D_MINUS.value, grade[0].value)

    def test_fastmail(self):
        grade = grade_spf(('v=spf1 include:spf.messagingengine.com -all',), 'dnstats.io')
        self.assertEqual(Grade.A.value, grade[0].value)

    def test_many_spf_records(self):
        grade = grade_spf(('v=spf1 -all','v=spf1 -all'), 'example.com')
        self.assertEqual(Grade.F.value, grade[0].value)

if __name__ == '__main__':
    unittest.main()
