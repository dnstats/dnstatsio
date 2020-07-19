import unittest

from grading.dmarc import grade as grade_dmarc


class TestDmarc(unittest.TestCase):
    def test_invalid(self):
        grade = grade_dmarc('tacos', 'example.com')
        self.assertEqual(grade, 0)

    def test_reject(self):
        grade = grade_dmarc('v=DMARC1; p=reject;', 'example.com')
        self.assertEqual(grade, 80)

    def test_quan(self):
        grade = grade_dmarc('v=DMARC1; p=quarantine;', 'example.com')
        self.assertEqual(grade, 45)

    def test_pct_reject_100(self):
        grade = grade_dmarc('v=DMARC1; p=reject; pct=100', 'example.com')
        self.assertEqual(grade, 80)

    def test_no_policy(self):
        grade = grade_dmarc('v=DMARC1;', 'example.com')
        self.assertEqual(grade, 0)

