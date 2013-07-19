# -*- coding: utf-8 -*-

import unittest
from models import BulkImport

class TestImportSpreadhseet(unittest.TestCase):

    def setUp(self):
        pass

    def test_creation_with_spreadsheet_key_raises_KeyError(self):
        with self.assertRaises(KeyError):
            BulkImport(spreadsheet_key='abc123')


if __name__ == '__main__':
    unittest.main()
