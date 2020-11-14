import unittest

from dnstats.grading.soa import grade

class TestSoa(unittest.TestCase):
    def test_normal_soa(self):
        result_grade = grade(['ns1.dnsimple.com. admin.dnsimple.com. 1574563989 86400 7200 604800 300'], 'dnstats.io')[0]
        self.assertEqual(result_grade, 100)

    def test_soa_neg(self):
        result_grade = grade(['ns1.dnsimple.com. admin.dnsimple.com. -1574563989 86400 7200 604800 300'], 'dnstats.io')[0]
        self.assertEqual(result_grade, 95)

    def test_soa_invalid(self):
        result_grade = grade(['ns1.dnsimple.com. admin.dnsimple.com. taco 86400 7200 604800 300'], 'dnstats.io')[0]
        self.assertEqual(result_grade, 95)

    def test_soa_missing_thing(self):
        result_grade = grade(['ns1.dnsimple.com. admin.dnsimple.com. taco 86400 7200 604800'], 'dnstats.io')[0]
        self.assertEqual(result_grade, 0)

    def test_soa_missing_things(self):
        result_grade = grade(['ns1.dnsimple.com. admin.dnsimple.com. taco 86400 7200'], 'dnstats.io')[0]
        self.assertEqual(result_grade, 0)

    def test_no_soa(self):
        result_grade = grade(['ns1.dnsimple.com. admin.dnsimple.com. taco 86400 7200'], 'dnstats.io')[0]
        self.assertEqual(result_grade, 0)

    def test_ip_list(self):
        result_grade = grade(['1.1.1.1', '8.8.8.8'], 'dnstats.io')[0]
        self.assertEqual(result_grade, 0)

    def test_taco(self):
        result_grade = grade(['taco'], 'dnstats.io')[0]
        self.assertEqual(result_grade, 0)


if __name__ == '__main__':
    unittest.main()
