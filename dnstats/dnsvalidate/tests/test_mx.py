import unittest

from dnstats.dnsvalidate.mx import Mx, MXErrors


class TestMx(unittest.TestCase):
    def test_no_mx(self):
        records = list()
        mx = Mx(records)
        expected_errors = [MXErrors.NO_MX_RECORDS]
        self.assertEqual(expected_errors, mx.errors)

    def test_one_valid_one_not(self):
        records = ['10 mail.dnstats.io.', 'taco dnstats.io.']
        mx = Mx(records)
        expected_errors = [MXErrors.INVALID_PREFERENCE]
        self.assertEqual(expected_errors, mx.errors)
        self.assertEqual(1, len(mx.valid_mx_records))

    def test_one_not_one_valid(self):
        records = ['taco dnstats.io.', '10 mail.dnstats.io.']
        mx = Mx(records)
        expected_errors = [MXErrors.INVALID_PREFERENCE]
        self.assertEqual(expected_errors, mx.errors)
        self.assertEqual(1, len(mx.valid_mx_records))

    def test_one_valid(self):
        records = ['10 mail.dnstats.io.']
        mx = Mx(records)
        expected_errors = list()
        self.assertEqual(expected_errors, mx.errors)
        self.assertEqual(1, len(mx.valid_mx_records))

    def test_two_valid(self):
        records = ['10 mail.dnstats.io.', '20 mail2.dnstats.io.']
        mx = Mx(records)
        expected_errors = list()
        self.assertEqual(expected_errors, mx.errors)
        self.assertEqual(2, len(mx.valid_mx_records))

    def test_one_invalid_preference(self):
        records = ['taco mail.dnstats.io.']
        mx = Mx(records)
        expected_errors = [MXErrors.INVALID_PREFERENCE]
        self.assertEqual(expected_errors, mx.errors)
        self.assertEqual(0, len(mx.valid_mx_records))

    def test_one_invalid_exchange(self):
        records = ['10 123']
        mx = Mx(records)
        expected_errors = [MXErrors.INVALID_EXCHANGE]
        self.assertEqual(expected_errors, mx.errors)
        self.assertEqual(0, len(mx.valid_mx_records))

    def test_two_invalid_exchange(self):
        records = ['10 123', '20 ']
        mx = Mx(records)
        expected_errors = [MXErrors.INVALID_EXCHANGE, MXErrors.INVALID_EXCHANGE]
        self.assertEqual(expected_errors, mx.errors)
        self.assertEqual(0, len(mx.valid_mx_records))

    def test_just_preference(self):
        records = ['10']
        mx = Mx(records)
        expected_errors = [MXErrors.TOO_FEW_PARTS]
        self.assertEqual(expected_errors, mx.errors)
        self.assertEqual(0, len(mx.valid_mx_records))

    def test_too_many_parts(self):
        records = ['10 10 10']
        mx = Mx(records)
        expected_errors = [MXErrors.TOO_MANY_PARTS]
        self.assertEqual(expected_errors, mx.errors)
        self.assertEqual(0, len(mx.valid_mx_records))

    def test_exchange_ip4(self):
        records = ['10 172.104.25.239']
        mx = Mx(records)
        expected_errors = [MXErrors.EXCHANGE_IS_AN_IP]
        self.assertEqual(expected_errors, mx.errors)
        self.assertEqual(0, len(mx.valid_mx_records))

    def test_exchange_ip4_int(self):
        records = ['10 10.1.1.1']
        mx = Mx(records)
        expected_errors = [MXErrors.EXCHANGE_IS_AN_IP]
        self.assertEqual(expected_errors, mx.errors)
        self.assertEqual(0, len(mx.valid_mx_records))

    def test_exchange_ip6_int(self):
        records = ['10 2600:3c03::f03c:92ff:feb0:7de']
        mx = Mx(records)
        expected_errors = [MXErrors.EXCHANGE_IS_AN_IP]
        self.assertEqual(expected_errors, mx.errors)
        self.assertEqual(0, len(mx.valid_mx_records))

    def test_two_invalid_preference(self):
        records = ['taco mail.dnstats.io.', 'taco mail.dnstats.io.']
        mx = Mx(records)
        expected_errors = [MXErrors.INVALID_PREFERENCE, MXErrors.INVALID_PREFERENCE]
        self.assertEqual(expected_errors, mx.errors)
        self.assertEqual(0, len(mx.valid_mx_records))

    def test_one_invalid_tld(self):
        records = ['10 mail.dnstats.lan.']
        mx = Mx(records)
        expected_errors = [MXErrors.NOT_PUBLIC_DOMAIN]
        self.assertEqual(expected_errors, mx.errors)
        self.assertEqual(0, len(mx.valid_mx_records))

    def test_one_no_end_dot(self):
        records = ['10 mail.dnstats.io']
        mx = Mx(records)
        expected_errors = [MXErrors.POSSIBLE_BAD_EXCHANGE]
        self.assertEqual(expected_errors, mx.errors)
        self.assertEqual(1, len(mx.valid_mx_records))


