#!/usr/bin/python3
# -*- encoding: utf-8 -*-
import unittest
from model import *
from example_data import expenses, payments, participations, persons, events


kasse = Gruppenkasse.create_new()
kasse.fill_with(expenses, payments, participations)

class TestGruppenkasse(unittest.TestCase):
    def setUp(self):
        ...

    def test_persons(self):
        person_names = list(map(lambda p: p.name, kasse.persons))

        for name in person_names:
            self.assertTrue(name in persons, msg=name)

    def test_events(self):
        print(kasse.person_dict)
        event_names = list(map(lambda p: p.name, kasse.events))

        for name in event_names:
            self.assertTrue(name in events, msg=name)

        for name in events:
            self.assertTrue(name in event_names, msg=name)

    def test_event(self):
        for event in kasse.events:
            ...#print(event)

    def test_person(self):
        for person in kasse.persons:
            print(person, "\t{:5.2f}".format(person.balance / 100))

    def test_payments(self):
        print(kasse.payments)



if __name__ == '__main__':
    unittest.main()
