#!/usr/bin/python3
# -*- encoding: utf-8 -*-
from collections import namedtuple
from decimal import *
getcontext().prec = 2


class Model(object):
    def __repr__(self):
        return repr(self.__dict__)
        

class Fund(Model):
    def __init__(self, events=[]):
        self.events = events

    def add_event(self, event):
        assert isinstance(event, Event)
        self.events.append(event)

    @property
    def persons(self):
        p = []
        for event in self.events:
            p.extend(event.participants)
        return set(p)

class Event(Model):
    def __init__(self, name, participants=[], expenses=[]):
        self.name = name
        self.participants = participants
        self.expenses = expenses

    @property
    def costs(self):
        return sum(map(lambda exp: exp.amount, self.expenses))

    def add_participant(self, person):
        assert isinstance(person, Person)
        self.participants.append(person)

    def add_expense(self, expense):
        assert isinstance(expense, Expense)
        self.expenses.append(expense)

class Person(Model):
    def __init__(self, name):
        self.name = name

class Expense(Model):
    def __init__(self, name, amount):
        self.name = name
        self.amount = Decimal(amount)




 

