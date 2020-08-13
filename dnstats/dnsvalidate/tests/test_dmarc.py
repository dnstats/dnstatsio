import unittest

from dnsvalidate.dmarc import Dmarc, DmarcErrors


class TestDmarc(unittest.TestCase):
    def test_ramdom_text(self):
        d = list()
        d.append('taco')
        dmarc_record = Dmarc(d)
        self.assertFalse(dmarc_record.is_valid)
        self.assertTrue(dmarc_record.errors.__contains__(DmarcErrors.INVALID_DMARC_RECORD_START))
