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

        record = ['v=DMARC1;']
        bimi = Bimi(record, self.dmarc)
        self.assertEqual([BimiErrors.INVALID_START], bimi.errors)

    def test_duplicate_tags(self):
        record = ['v=BIMI1; v=BIMI1;']
        bimi = Bimi(record, self.dmarc)
        self.assertEqual([BimiErrors.DUPLICATE_TAG_FOUND, BimiErrors.LOGO_NOT_DEFINED, BimiErrors.SELECTOR_NOT_DEFINED], bimi.errors)


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

    def test_with_none_dmarc(self):
        record = ['v=BIMI1; l=https://dnstats.io/logo.svg; s=transaction']
        dmarc = ['v=DMARC1; p=none']
        bimi = Bimi(record, dmarc)
        self.assertEqual([BimiErrors.DMARC_STRICT_ENOUGH_POLICY], bimi.errors)

    def test_with_quarantine(self):
        record = ['v=BIMI1; l=https://dnstats.io/logo.svg; s=transaction']
        dmarc = ['v=DMARC1; p=quarantine']
        bimi = Bimi(record, dmarc)
        self.assertEqual([], bimi.errors)

    def test_with_quarantine_bad_percent(self):
        record = ['v=BIMI1; l=https://dnstats.io/logo.svg; s=transaction']
        dmarc = ['v=DMARC1; p=quarantine; pct=10']
        bimi = Bimi(record, dmarc)
        self.assertEqual([BimiErrors.DMARC_STRICT_ENOUGH_PERCENT], bimi.errors)

    def test_with_no_dmarc(self):
        record = ['v=BIMI1; l=https://dnstats.io/logo.svg; s=transaction']
        dmarc = []
        bimi = Bimi(record, dmarc)
        self.assertEqual([BimiErrors.DMARC_NOT_DEFINED, BimiErrors.DMARC_STRICT_ENOUGH_POLICY], bimi.errors)

