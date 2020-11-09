import unittest
from dnstats.dnsvalidate.soa import Soa, SoaErrors


class TestNs(unittest.TestCase):
    def test_normal_soa(self):
        result = Soa(['ns1.dnsimple.com. admin.dnsimple.com. 1574563989 86400 7200 604800 300'], 'dnstats.io')
        self.assertEqual(0, len(result.errors))
    
    def test_soa_neg(self):
        result = Soa(['ns1.dnsimple.com. admin.dnsimple.com. -1574563989 86400 7200 604800 300'], 'dnstats.io')
        self.assertNotEqual(0, len(result.errors))

    def test_soa_invalid(self):
        result = Soa(['ns1.dnsimple.com. admin.dnsimple.com. taco 86400 7200 604800 300'], 'dnstats.io')
        self.assertNotEqual(0, len(result.errors))

