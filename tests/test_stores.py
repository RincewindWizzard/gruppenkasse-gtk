#!/usr/bin/python3
# -*- encoding: utf-8 -*-
import unittest
import model, example_data
from model import fill_store
""" 
* Uses the ListStores in model.py and fills them with the example data from example_data.py (which is private, i will supply some random data soon)
"""

class TestListStore(unittest.TestCase):

    def test_transfers(self):
        store = model.transfers
        data = example_data.transfers
        fill_store(store, data)

    def test_expenses(self):
        store = model.expenses
        data = example_data.expenses
        fill_store(store, data)

    def test_persons(self):
        store = model.persons
        data = example_data.persons
        fill_store(store, data)

    def test_participations(self):
        store = model.participations
        data = example_data.participations
        fill_store(store, data)


if __name__ == '__main__':
    unittest.main()
