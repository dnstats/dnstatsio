import unittest

from dnstats.grading.mx import grade as grade_mx


class TestMx(unittest.TestCase):
    def test_no_mx(self):
        records = list()
        grade, errors = grade_mx(records, 'dnstats.io')
        self.assertEqual(0, grade)

    def test_one_valid_one_not(self):
        records = ['10 mail.dnstats.io.', 'taco dnstats.io.']
        grade, errors = grade_mx(records, 'dnstats.io')
        self.assertEqual(50, grade)

    def test_one_not_one_valid(self):
        records = ['taco dnstats.io.', '10 mail.dnstats.io.']
        grade, errors = grade_mx(records, 'dnstats.io')
        self.assertEqual(50, grade)

    def test_one_valid(self):
        records = ['10 mail.dnstats.io.']
        grade, errors = grade_mx(records, 'dnstats.io')
        self.assertEqual(100, grade)

    def test_two_valid(self):
        records = ['10 mail.dnstats.io.', '20 mail2.dnstats.io.']
        grade, errors = grade_mx(records, 'dnstats.io')
        self.assertEqual(100, grade)

    def test_one_invalid_preference(self):
        records = ['taco mail.dnstats.io.']
        grade, errors = grade_mx(records, 'dnstats.io')
        self.assertEqual(0, 0)

    def test_one_invalid_exchange(self):
        records = ['10 123']
        grade, errors = grade_mx(records, 'dnstats.io')
        self.assertEqual(0, grade)

    def test_two_invalid_exchange(self):
        records = ['10 123', '20 ']
        grade, errors = grade_mx(records, 'dnstats.io')
        self.assertEqual(0, grade)

    def test_just_preference(self):
        records = ['10']
        grade, errors = grade_mx(records, 'dnstats.io')
        self.assertEqual(0, grade)

    def test_too_many_parts(self):
        records = ['10 10 10']
        grade, errors = grade_mx(records, 'dnstats.io')
        self.assertEqual(0, grade)

    def test_exchange_ip4(self):
        records = ['10 172.104.25.239']
        grade, errors = grade_mx(records, 'dnstats.io')
        self.assertEqual(0, grade)

    def test_exchange_ip4_int(self):
        records = ['10 10.1.1.1']
        grade, errors = grade_mx(records, 'dnstats.io')
        self.assertEqual(0, grade)

    def test_exchange_ip6_int(self):
        records = ['10 2600:3c03::f03c:92ff:feb0:7de']
        grade, errors = grade_mx(records, 'dnstats.io')
        self.assertEqual(0, grade)

    def test_two_invalid_preference(self):
        records = ['taco mail.dnstats.io.', 'taco mail.dnstats.io.']
        grade, errors = grade_mx(records, 'dnstats.io')
        self.assertEqual(0, grade)

    def test_one_invalid_tld(self):
        records = ['10 mail.dnstats.lan.']
        grade, errors = grade_mx(records, 'dnstats.io')
        self.assertEqual(0, grade)

    def test_one_no_end_dot(self):
        records = ['10 mail.dnstats.io']
        grade, errors = grade_mx(records, 'dnstats.io')
        self.assertEqual(95, grade)

