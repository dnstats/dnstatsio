import unittest

import dnstats.utils.aws


class TestAWS(unittest.TestCase):
    def test_filename_json(self):
        self.assertEqual('application/json', dnstats.utils.aws._get_mime_type_from_filename('taco.json'))

    def test_filename_csv(self):
        self.assertNotEqual('application/json', dnstats.utils.aws._get_mime_type_from_filename('taco.csv'))
        self.assertEqual('text/csv', dnstats.utils.aws._get_mime_type_from_filename('taco.csv'))
