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

    def test_bad_tag(self):
        output = validate_caa(['0 t@aco taco'], 'example.com')
        self.assertEqual(output['errors'], [CAAErrors.INVALID_TAG])

    def test_too_many_quotes(self):
        output = validate_caa(['0 issue ""taco"'], 'example.com')
        self.assertEqual(output['errors'], [CAAErrors.VALUE_QUOTE_ERROR])

    def test_too_few_quotes(self):
        output = validate_caa(['0 issue "taco'], 'example.com')
        self.assertEqual(output['errors'], [CAAErrors.VALUE_QUOTE_ERROR])

    def test_not_quoted(self):
        output = validate_caa(['0 issue taco taco'], 'example.com')
        self.assertEqual(output['errors'], [CAAErrors.VALUE_NOT_QUOTED])
        self.assertEqual(0, len(output['iodef']))
        self.assertEqual(0, len(output['issue']))
        self.assertEqual(0, len(output['issuewild']))

    def test_issue(self):
        output = validate_caa(['0 issue dnstats.io'], 'example.com')
        self.assertEqual(output['errors'], [])
        self.assertEqual(0, len(output['iodef']))
        self.assertEqual(1, len(output['issue']))
        self.assertEqual(0, len(output['issuewild']))

    def test_wildissue_quoted(self):
        output = validate_caa(['0 issuewild "dnstats.io"'], 'example.com')
        self.assertEqual(output['errors'], [])

    def test_wildissue_quoted_semi(self):
        output = validate_caa(['0 issuewild "dnstats.io; value=taco"'], 'example.com')
        self.assertEqual(output['errors'], [])
        self.assertEqual(0, len(output['iodef']))
        self.assertEqual(0, len(output['issue']))
        self.assertEqual(1, len(output['issuewild']))

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
        self.assertEqual(1, len(output['iodef']))
        self.assertEqual(0, len(output['issue']))
        self.assertEqual(0, len(output['issuewild']))

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

    def test_iodef_web_issue(self):
        output = validate_caa(['0 iodef https://dnstats.io/caa', '0 issue dnstats.io'], 'example.com')
        self.assertEqual(output['errors'], [])
        self.assertEqual(1, len(output['iodef']))
        self.assertEqual(1, len(output['issue']))
        self.assertEqual(0, len(output['issuewild']))

    def test_iodef_web_issue_issuewild(self):
        output = validate_caa(['0 iodef https://dnstats.io/caa', '0 issue dnstats.io', '0 issuewild dnstats.io'], 'example.com')
        self.assertEqual(output['errors'], [])
        self.assertEqual(1, len(output['iodef']))
        self.assertEqual(1, len(output['issue']))
        self.assertEqual(1, len(output['issuewild']))

    def test_iodef_web_block_all(self):
        output = validate_caa(['0 iodef https://dnstats.io/caa', '0 issue ;', '0 issuewild ;'], 'example.com')
        self.assertEqual(output['errors'], [])
        self.assertEqual(1, len(output['iodef']))
        self.assertEqual(1, len(output['issue']))
        self.assertEqual(1, len(output['issuewild']))

    def test_netfilx(self):
        caa = ['0 issue "digicert.com"', '0 issue "letsencrypt.org"', '0 issuewild "digicert.com"',
               '0 issuewild "letsencrypt.org"', '0 iodef "mailto:security@netflix.com"']
        output = validate_caa(caa, 'example.com')
        self.assertEqual(output['errors'], [])
        self.assertEqual(1, len(output['iodef']))
        self.assertEqual(2, len(output['issue']))
        self.assertEqual(2, len(output['issuewild']))