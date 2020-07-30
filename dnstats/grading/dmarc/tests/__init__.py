import unittest

from grading.dmarc import grade as grade_dmarc


class TestDmarc(unittest.TestCase):
    def test_invalid(self):
        grade = grade_dmarc('tacos', 'example.com')
        self.assertEqual(grade, 0)

    def test_reject(self):
        grade = grade_dmarc('v=DMARC1; p=reject;', 'example.com')
        self.assertEqual(grade, 80)

    def test_bad_policy(self):
        grade = grade_dmarc('v=DMARC1; p=tacoman;', 'example.com')
        self.assertEqual(grade, 0)

    def test_quan(self):
        grade = grade_dmarc('v=DMARC1; p=quarantine;', 'example.com')
        self.assertEqual(grade, 45)

    def test_pct_reject_100(self):
        grade = grade_dmarc('v=DMARC1; p=reject; pct=100', 'example.com')
        self.assertEqual(grade, 80)

    def test_pct_reject_0(self):
        grade = grade_dmarc('v=DMARC1; p=reject; pct=0', 'example.com')
        self.assertEqual(grade, 73)

    def test_pct_reject_50(self):
        grade = grade_dmarc('v=DMARC1; p=reject; pct=50', 'example.com')
        self.assertEqual(grade, 76)

    def test_no_policy(self):
        grade = grade_dmarc('v=DMARC1;', 'example.com')
        self.assertEqual(grade, 0)

    def test_reject_with_rua(self):
        grade = grade_dmarc('v=DMARC1; p=reject; rua=mailto:postmaster@dnstats.io', 'google.com')
        self.assertEqual(grade, 85)

    def test_perfect_score(self):
        grade = grade_dmarc('v=DMARC1; adkim=s; aspf=s; fo=1; p=reject; rua=mailto:postmaster@dnstats.io; ruf=mailto:postmaster@dnstats.io', 'google.com')
        self.assertEqual(grade, 104)

    def test_invalid_tag(self):
        grade = grade_dmarc('v=DMARC1; hello=p', 'example.com')
        self.assertEqual(grade, 0)
