#!/usr/bin/python3
# -*- encoding: utf-8 -*-
import unittest
import model
import example_data as ex
from model import GruppenkasseStore
""" 
* Uses the ListStores in model.py and fills them with the example data from example_data.py (which is private, i will supply some random data soon)
"""

class TestListStore(unittest.TestCase):
    def setUp(self):
        store = GruppenkasseStore(ex.transfers, ex.expenses, ex.persons, ex.participations)

    def test_transfers(self):
        ...


if __name__ == '__main__':
    unittest.main()
