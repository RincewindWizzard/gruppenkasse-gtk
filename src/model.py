#!/usr/bin/python3
# -*- encoding: utf-8 -*-
import inspect
from datetime import datetime
from sqlalchemy import Table, Column, Date, String, Integer, Float, ForeignKey, func, create_engine
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy import inspect as sqlinspect





datefmt = '%d.%m.%y'
 
Base = declarative_base()
def __repr__(self):
    all_members = dir(self)
    members = []
    for k in all_members:
        if not k[0] == '_':
            members.append(k)

    return "{}({})".format(
        self.__class__.__name__, 
        ", ".join([
            "{}={}".format(
                k, 
                repr(getattr(self, k))) 
                for k in members
    ]))
#Base.__repr__ = __repr__

 
 
class Person(Base):
    __tablename__ = 'persons'
    id   = Column(Integer, primary_key=True) 
    name = Column(String, unique=True)

    @property
    def expenses(self):
        result = 0
        for event in self.events:
            result += event.expense_per_participant

        return int(result)

    @property
    def payed(self):
        result = 0
        for payment in self.payments:
            result += payment.amount
        return int(result)

    @property
    def balance(self):
        return self.payed - self.expenses

    def __repr__(self):
        return repr(self.name)

    def __str__(self):
        return self.name



class Participation(Base):
    __tablename__ = 'participations'
    person = Column(Integer, ForeignKey('persons.id'), primary_key=True)
    event  = Column(Integer, ForeignKey('events.id'), primary_key=True)


class Event(Base):
    __tablename__ = 'events'
    id          = Column(Integer, primary_key=True) 
    name         = Column(String, unique=True)
    participants = relationship("Person",
                       secondary='participations',
                       backref="events")

    @property
    def expense_per_participant(self):
        return (self.expense_sum) / len(self.participants)

    @property
    def expense_sum(self):
        session = sqlinspect(self).session
        result = session.query(func.sum(Expense.amount)).filter(Expense.event == self).scalar()
        return result if result else 0

    def __repr__(self):
        return "Event(name={}, participants={}, expense_sum={:.2f} €, per_participant={:.2f} €)".format(
            repr(self.name),
            len(self.participants),
            self.expense_sum / 100,
            self.expense_per_participant / 100
        )

    def __str__(self):
        return repr(self)
 
class Payment(Base):
    __tablename__ = 'payments'
    id          = Column(Integer, primary_key=True) 
    date        = Column(Date)
    person_id   = Column(Integer, ForeignKey('persons.id'))
    person      = relationship("Person", backref="payments")
    amount      = Column(Integer) # in euro cents
    description = Column(String)

    def __repr__(self):
        return "Payment({}, {}, {:.2f} €, {})".format(
            repr(datetime.strftime(self.date, datefmt)),
            repr(self.person),
            self.amount / 100,
            repr(self.description)
        )

    def __str__(self):
        return self.name

class Expense(Base):
    __tablename__ = 'expenses'
    id          = Column(Integer, primary_key=True) 
    date        = Column(Date)
    event_id    = Column(Integer, ForeignKey('events.id'))
    event       = relationship("Event", backref="expenses")
    amount      = Column(Integer) # in euro cents
    description = Column(String)

    def __repr__(self):
        return "Expense({}, {}, {:.2f} €, {})".format(
            repr(datetime.strftime(self.date, datefmt)),
            repr(self.event),
            self.amount / 100,
            repr(self.description)
        )

    def __str__(self):
        return self.name


class Gruppenkasse(object):
    @staticmethod
    def create_new(path=None):
        if path:
            engine = create_engine('sqlite://'+path)
        else:
            engine = create_engine('sqlite://')
        Session = sessionmaker()
        Session.configure(bind=engine)
        Base.metadata.create_all(engine)
        return Gruppenkasse(Session())

    def __init__(self, session):
        self.db = session

    @property
    def events(self):
        return self.db.query(Event).all()

    @property
    def event_dict(self):
        events = {}
        for event in self.db.query(Event).all():
            events[event.name] = event
        return events

    @property
    def person_dict(self):
        persons = {}
        for person in self.db.query(Person).all():
            persons[person.name] = person
        return persons

    @property
    def persons(self):
        return self.db.query(Person).all()

    @property
    def payments(self):
        return self.db.query(Payment).all()

    # Shortcut functions disguising sqlalchemy backend
    def new_person(self, name):
        p = Person(name=name)
        self.db.add(p)
        return p

    def new_event(self, name):
        event = Event(name=name)
        self.db.add(event)
        return event

    def new_payment(self, date, person, amount, description):
        if isinstance(person, str):
            person = self.person_dict[person]
        payment = Payment(date=date, person=person, amount=amount, description=description)
        self.db.add(payment)
        return payment


    def fill_with(self, expenses, payments, participations):
        persons = []
        events = []
        for participation in participations:
            events.append(participation[0])
            persons.append(participation[1])

        persons = set(persons)
        events = set(events)


        for name in persons:
            self.new_person(name)

        for name in events:
            self.new_event(name)

        for event, person in participations:
            person = self.db.query(Person).filter(Person.name == person).first()
            event = self.db.query(Event).filter(Event.name == event).first()
            event.participants.append(person)

        for date, person, amount, description in payments:
            person = self.db.query(Person).filter(Person.name == person).first()
            self.db.add(Payment(date=date, person=person, amount=int(amount*100), description=description))

        for date, event, amount, description in expenses:
            event = self.db.query(Event).filter(Event.name == event).first()
            self.db.add(Expense(date=date, event=event, amount=int(amount*100), description=description))

        self.db.commit()


#def expense_of_event(event):
#    return s.query(func.sum(Expense.amount).label("payed")).filter(Expense.event == event).scalar()


