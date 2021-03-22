import unittest

from dnstats.dnsvalidate.bimi import Bimi, BimiErrors


class TestBimi(unittest.TestCase):
    dmarc = ['v=DMARC1; p=reject']
    def test_opt_out(self):
       record = ['v=BIMI1; l=; s=;']
       bimi = Bimi(record, self.dmarc)
       self.assertEqual([BimiErrors.BIMI_OPTED_OUT], bimi.errors)


    def test_broken_records(self):
        record = ['v=BIMI1; l;= s=;']
        bimi = Bimi(record, self.dmarc)
        self.assertEqual([BimiErrors.LOGO_NOT_DEFINED, BimiErrors.SELECTOR_NOT_DEFINED], bimi.errors)

        record = ['v=BIMI1; l;= s;']
        bimi = Bimi(record, self.dmarc)
        self.assertEqual([BimiErrors.LOGO_NOT_DEFINED, BimiErrors.SELECTOR_NOT_DEFINED], bimi.errors)

        record = ['v=BIMI1; l;= s;;']
        bimi = Bimi(record, self.dmarc)
        self.assertEqual([BimiErrors.LOGO_NOT_DEFINED, BimiErrors.SELECTOR_NOT_DEFINED], bimi.errors)

        record = ['v=BIMI1; l']
        bimi = Bimi(record, self.dmarc)
        self.assertEqual([BimiErrors.LOGO_NOT_DEFINED, BimiErrors.SELECTOR_NOT_DEFINED], bimi.errors)

        record = ['v=BIMI1; s']
        bimi = Bimi(record, self.dmarc)
        self.assertEqual([BimiErrors.LOGO_NOT_DEFINED, BimiErrors.SELECTOR_NOT_DEFINED], bimi.errors)

        record = ['v=BIMI1; ; ; ; ;']
        bimi = Bimi(record, self.dmarc)
        self.assertEqual([BimiErrors.LOGO_NOT_DEFINED, BimiErrors.SELECTOR_NOT_DEFINED], bimi.errors)

        record = ['v=BIMI1;']
        bimi = Bimi(record, self.dmarc)
        self.assertEqual([BimiErrors.LOGO_NOT_DEFINED, BimiErrors.SELECTOR_NOT_DEFINED], bimi.errors)



    def test_default(self):
        record = ['v=BIMI1; l=https://dnstats.io/logo.svg']
        bimi = Bimi(record, self.dmarc)
        self.assertEqual([BimiErrors.SELECTOR_NOT_DEFINED], bimi.errors)

    def test_with_selector(self):
        record = ['v=BIMI1; l=https://dnstats.io/logo.svg; s=transaction;']
        bimi = Bimi(record, self.dmarc)
        self.assertEqual([], bimi.errors)


    def test_with_selector_no_logo(self):
        record = ['v=BIMI1; l=; s=transaction']
        bimi = Bimi(record, self.dmarc)
        self.assertEqual([BimiErrors.LOGO_LOCATION_BLANK], bimi.errors)


    def test_with_bad_logo_location(self):
        record = ['v=BIMI1; l=dnstats.io/logo.svg; s=transaction']
        bimi = Bimi(record, self.dmarc)
        self.assertEqual([BimiErrors.LOGO_INVALID_LOCATION], bimi.errors)


    def test_with_http_logo(self):
        record = ['v=BIMI1; l=http://dnstats.io/logo.svg; s=transaction']
        bimi = Bimi(record, self.dmarc)
        self.assertEqual([BimiErrors.LOGO_NOT_HTTPS], bimi.errors)

    def test_with_bad_logo_format(self):
        record = ['v=BIMI1; l=https://dnstats.io/logo.jpg; s=transaction']
        bimi = Bimi(record, self.dmarc)
        self.assertEqual([BimiErrors.LOGO_INVALID_FORMAT], bimi.errors)