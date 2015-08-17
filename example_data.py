#!/usr/bin/python3
# -*- encoding: utf-8 -*-
from model import *

kasse = Fund()
wacken = Event("Wacken")
for name in ["Michael", "Alice", "Bob", "Mallory"]:
    wacken.add_participant(Person(name))
kasse.add_event(wacken)

wacken.add_expense(Expense("Benzin", 50))


