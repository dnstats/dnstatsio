import unittest

from dnstats.dnsvalidate.dmarc import Dmarc, DmarcErrors


class TestDmarc(unittest.TestCase):
    def test_ramdom_text(self):
        d = ['taco']
        dmarc_record = Dmarc(d)
        self.assertFalse(dmarc_record.is_valid)
        self.assertTrue(dmarc_record.errors.__contains__(DmarcErrors.INVALID_DMARC_RECORD_START))

    def test_blank(self):
        d = list()
        dmarc_record = Dmarc(d)
        self.assertFalse(dmarc_record.is_valid)
        self.assertTrue(dmarc_record.errors.__contains__(DmarcErrors.NO_DMARC_RECORD))