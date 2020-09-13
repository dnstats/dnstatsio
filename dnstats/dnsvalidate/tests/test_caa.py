import unittest

from dnstats.dnsvalidate.caa import validate as validate_caa
from dnstats.dnsvalidate.caa import CAAErrors


class TestCaa(unittest.TestCase):
    def test_no_caa(self):
        output = validate_caa(list(), 'example.com')
        self.assertEqual(output['errors'], [CAAErrors.NO_CAA_RECORDS])

    def test_invalid_record(self):
        output = validate_caa(['taco'], 'example.com')
        self.assertEqual(output['errors'], [CAAErrors.INVALID_PROPERTY_STRUCTURE])

    def test_invalid_record2(self):
        output = validate_caa(['taco taco taco'], 'example.com')
        self.assertEqual(output['errors'], [CAAErrors.INVALID_FLAG])

    def test_invalid_flag(self):
        output = validate_caa(['1000 taco taco'], 'example.com')
        self.assertEqual(output['errors'], [CAAErrors.INVALID_FLAG])

    def test_too_long_tag(self):
        output = validate_caa(['0 tacotacotacotaco taco'], 'example.com')
        self.assertEqual(output['errors'], [CAAErrors.TAG_TOO_LONG])

    def test_too_many_quotes(self):
        output = validate_caa(['0 issue ""taco"'], 'example.com')
        self.assertEqual(output['errors'], [CAAErrors.VALUE_QUOTE_ERROR])

    def test_too_few_quotes(self):
        output = validate_caa(['0 issue "taco'], 'example.com')
        self.assertEqual(output['errors'], [CAAErrors.VALUE_QUOTE_ERROR])

    def test_not_quoted(self):
        output = validate_caa(['0 issue taco taco'], 'example.com')
        self.assertEqual(output['errors'], [CAAErrors.VALUE_NOT_QUOTED])

    def test_issue(self):
        output = validate_caa(['0 issue dnstats.io'], 'example.com')
        self.assertEqual(output['errors'], [])

    def test_wildissue_quoted(self):
        output = validate_caa(['0 issuewild "dnstats.io"'], 'example.com')
        self.assertEqual(output['errors'], [])

    def test_wildissue_quoted_semi(self):
        output = validate_caa(['0 issuewild "dnstats.io; value=taco"'], 'example.com')
        self.assertEqual(output['errors'], [])

    def test_issue_quoted_semi(self):
        output = validate_caa(['0 issue "dnstats.io; value=taco"'], 'example.com')
        self.assertEqual(output['errors'], [])

    def test_wildissue(self):
        output = validate_caa(['0 issuewild dnstats.io'], 'example.com')
        self.assertEqual(output['errors'], [])

    def test_issue_badhost(self):
        output = validate_caa(['0 issue dnstats,io'], 'example.com')
        self.assertEqual(output['errors'], [CAAErrors.ISSUE_DOMAIN_INVALID])

    def test_wildissue_badhost(self):
        output = validate_caa(['0 issuewild dnstats,io'], 'example.com')
        self.assertEqual(output['errors'], [CAAErrors.ISSUEWILD_DOMAIN_INVALID])

    def test_iodef_mail(self):
        output = validate_caa(['0 iodef mailto:caa@dnstats.io'], 'example.com')
        self.assertEqual(output['errors'], [])

    def test_iodef_web(self):
        output = validate_caa(['0 iodef https://dnstats.io/caa'], 'example.com')
        self.assertEqual(output['errors'], [])

    def test_iodef_mail_invalid(self):
        output = validate_caa(['0 iodef mailto:caa@dnstats,io'], 'example.com')
        self.assertEqual(output['errors'], [CAAErrors.IODEF_INVALID_EMAIL])

    def test_iodef_web_invalid(self):
        output = validate_caa(['0 iodef https://dnstats,io/caa'], 'example.com')
        self.assertEqual(output['errors'], [CAAErrors.IODEF_INVALID_URL])

    def test_iodef_no_mailto(self):
        output = validate_caa(['0 iodef caa@dnstats.io'], 'example.com')
        self.assertEqual(output['errors'], [CAAErrors.IODEF_NO_SCHEME])

    def test_iodef_bad_scheme(self):
        output = validate_caa(['0 iodef taco://dnstats.io/caa'], 'example.com')
        self.assertEqual(output['errors'], [CAAErrors.IODEF_NO_SCHEME])
