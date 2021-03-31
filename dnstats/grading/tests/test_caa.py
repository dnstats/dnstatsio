import unittest

from dnstats.grading.caa import grade as grade_caa


class TestCaa(unittest.TestCase):
    def test_no_caa(self):
        self.assertEqual(0, grade_caa([], 'example.com')[0])

    def test_one_issue(self):
        caas = ['0 issue "letsencrypt.org"']
        self.assertEqual(85, grade_caa(caas, 'example.com')[0])

    def test_two_issue(self):
        caas = ['0 issue "letsencrypt.org"', '0 issue "digicert.com"']
        self.assertEqual(85, grade_caa(caas, 'example.com')[0])

    def test_two_issue_iodef(self):
        caas = ['0 issue "letsencrypt.org"', '0 issue "digicert.com"', '0 iodef mailto:caa@dnstats.io']
        self.assertEqual(90, grade_caa(caas, 'example.com')[0])

    def test_two_issue_iodef_issuewild(self):
        caas = ['0 issue "letsencrypt.org"', '0 issue "digicert.com"', '0 iodef mailto:caa@dnstats.io', '0 issuewild ";"']
        self.assertEqual(100, grade_caa(caas, 'example.com')[0])

    def test_two_issue_bad_iodef_issuewild(self):
        caas = ['0 issue "letsencrypt.org"', '0 issue "digicert.com"', '0 iodef caa@dnstats.io', '0 issuewild ";"']
        self.assertEqual(93, grade_caa(caas, 'example.com')[0])
