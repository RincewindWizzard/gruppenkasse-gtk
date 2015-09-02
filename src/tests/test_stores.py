#!/usr/bin/python3
# -*- encoding: utf-8 -*-
import unittest
import model
from stores import SQLStore
""" 
* Uses the ListStores in model.py and fills them with the example data from example_data.py (which is private, i will supply some random data soon)
"""

kasse = model.Gruppenkasse("/home/dfl/Programmierung/Python/gruppenkasse-gtk/gruppenkasse.sqlite")

class TestSQLStore(unittest.TestCase):
    def test_persons(self):
        personen = kasse.db.query(model.Person)
        self.store_test(personen)
        self.store_test(personen.filter(model.Person.id % 2 == 0))

    def store_test(self, personen):
        data_func = lambda person: (person.id, person.name)
        store = SQLStore(
            personen, 
            data_func, 
            int, str
        )
        person_list = personen.all()
        for i, row in enumerate(person_list):
            row = data_func(row)
            for j,_ in enumerate(row):
                self.assertEqual(store[i][j], row[j])
        

if __name__ == '__main__':
    unittest.main()
