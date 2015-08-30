#!/usr/bin/python3
# -*- encoding: utf-8 -*-
import unittest
import model
import example_data as ex



class TestListStore(unittest.TestCase):
    def setUp(self):
        self.data = [("Johny", "Smith"), ("Jenny", "Smith"), ("John", "Doe"), ("Jane", "Doe")]
        self.store = ListModifier(self.data, 1, "Doe")

    def test_transfers(self):
        self.assertEqual(self.store[0][0], "John")
        self.assertEqual(self.store[1][0], "Jane")
        self.assertEqual(len(self.store), 2)
        self.store.append(["Marcus"])
        print(self.data)
        self.assertEqual(self.store[2][0], "Marcus")


if __name__ == '__main__':
    unittest.main()
