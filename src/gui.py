#!/usr/bin/python3
# -*- encoding: utf-8 -*-
from gi.repository import Gtk
from datetime import datetime
from decimal import Decimal
from model import Person

datefmt = '%d.%m.%y'

def strfmoney(amount: "int cents"):
    return "{:.2f} €".format(amount / 100).replace(".", ",")

def strpmoney(amount):
    amount = amount.replace("€", "").replace(",", ".")
    return int(Decimal(amount) * 100)

# this function is used to render ints as money string
def money_cell_renderer(column, cell, store, index, user_data):
    return store[index]



class PersonTab(object):
    def __init__(self, gui):
        self.kasse = gui.model
        builder = gui.builder
        self.person_listview = builder['person_list']
        self.person_listview.set_grid_lines(Gtk.TreeViewGridLines.BOTH)
        self.person_list = Gtk.ListStore(int, str, str, str, str)
        self.person_listview.set_model(self.person_list)
        self.person_listview.get_selection().connect('changed', self.person_selected)

        self.payments = builder['payments_store']
            
        self.update()

    def update(self):
        self.person_list.clear()
        for person in self.kasse.persons:
            self.person_list.append([person.id, person.name, strfmoney(person.payed), strfmoney(person.expenses), strfmoney(person.balance)])

    def person_selected(self, selection):
        model, index = selection.get_selected()
        person_id = model[index][0]

        
        person = self.kasse.db.query(Person).filter(Person.id == person_id).first()
        self.payments.clear()
        for payment in person.payments:
            self.payments.append([payment.id, datetime.strftime(payment.date, datefmt), strfmoney(payment.amount), payment.description])




class EventTab(object):
    def __init__(self, main_gui, kasse):
        self.kasse = kasse
        self.main_gui = main_gui

        builder = main_gui.builder
        self.event_listview = builder['event_list']
        self.event_list = Gtk.ListStore(int, str, int, str, str)
        self.event_listview.set_model(self.event_list)
        self.event_listview.get_selection().connect('changed', self.event_selected)

        self.participants = builder['participants_store']
        self.update()

    def update(self):
        self.event_list.clear()

        for event in self.kasse.events:
            self.event_list.append([event.id, event.name, len(event.participants), strfmoney(event.expense_sum), strfmoney(event.expense_per_participant)])

    def event_selected(self, selection):
        model, index = selection.get_selected()
        event_name = model[index][1]
        event = self.kasse.event_dict[event_name]
        self.main_gui.on_event_selected(event)

        self.participants.clear()
        for person in self.kasse.persons:
            self.participants.append([person.id, person.name, person in event.participants])



        

class GruppenkasseGui(object):
    glade_file = "./res/gruppenkasse.glade"
    def __init__(self, model):
        self.model = model
        self.builder = BuilderWrapper()
        self.builder.add_from_file(GruppenkasseGui.glade_file)

        self.event_tab = EventTab(self, self.model)
        self.person_tab = PersonTab(self)

        self.builder["main_window"].show_all()

        self.builder['person_list']

        # delete Event
        self.builder['main_window'].connect("delete-event", self.on_main_window_delete_event)

    def main(self):
        Gtk.main()

    #---------------------------------------------------------------------------
    # Signals
    def on_main_window_delete_event(self, *args):
        Gtk.main_quit(*args)

    def on_event_selected(self, event):
        expense_list = self.builder["expense_store"]
        expense_list.clear()

        for expense in event.expenses:
            expense_list.append([expense.id, datetime.strftime(expense.date, datefmt), "{:.2f} €".format(expense.amount / 100), str(expense.description)])


class BuilderWrapper(Gtk.Builder):
    """ Mimics a Python dict to access the widgets in a syntatic sugared way """
    def __getitem__(self, key):
        return self.get_object(key)
        
