import unittest

from dnstats.grading.bimi import grade as grade_bimi


class TestBimiGrading(unittest.TestCase):
    def test_valid(self):
        dmarc = ['v=DMARC1; p=reject']
        bimi = ['v=BIMI1; l=https://dnstast.io/logo.svg']
        grade, errors = grade_bimi(bimi, dmarc, 'dnstats.io')
        self.assertEqual(100, grade)

    def test_not_valid(self):
        dmarc = ['v=DMARC1; p=reject']
        bimi = ['v=BIMI1; l=http://dnstast.io/logo.svg']
        grade, errors = grade_bimi(bimi, dmarc, 'dnstats.io')
        self.assertEqual(0, grade)


