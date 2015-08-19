#!/usr/bin/python3
# -*- encoding: utf-8 -*-
import unittest
import model
import example_data as ex
from stores import CustomTreeModel, ListModifier
""" 
* Uses the ListStores in model.py and fills them with the example data from example_data.py (which is private, i will supply some random data soon)
"""

class TestListStore(unittest.TestCase):
    def setUp(self):
        self.data = [("Johny", "Smith", 1), ("Jenny", "Smith", 2), ("John", "Doe", 3), ("Jane", "Doe", 3)]
        self.store = CustomTreeModel(ListModifier(self.data, 1, "Doe"))

    def test_get(self):
        self.assertEqual(self.store[0][0], "John")
        self.assertEqual(self.store[1][0], "Jane")
        print(list(self.store[0]))

if __name__ == '__main__':
    unittest.main()
