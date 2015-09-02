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
        self.kasse = gui.kasse
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

        
        person = self.kasse.get_person(person_id)
        self.payments.clear()
        for payment in person.payments:
            self.payments.append([payment.id, datetime.strftime(payment.date, datefmt), strfmoney(payment.amount), payment.description])




class EventTab(object):
    def __init__(self, main_gui, kasse):
        self.kasse = kasse
        self.main_gui = main_gui

        self.event = None

        builder = main_gui.builder
        self.event_listview = builder['event_list']
        self.event_list = Gtk.ListStore(int, str, int, str, str)
        self.event_listview.set_model(self.event_list)
        self.event_listview.get_selection().connect('changed', self.event_selected)

        self.participants = builder['participants_store']
        self.expense_list = builder["expense_store"]

        self.participation_toggle = builder['participation_toggle']
        self.participation_toggle.connect("toggled", self.participation_toggled)
        builder['event_name_cell'].connect("edited", self.on_event_name_changed)

        #builder['add_expense'].connect("edited", self.on_add_expense)


        # add all events
        self.event_list.clear()
        for event in self.kasse.events:
            self.event_list.append([event.id, event.name, len(event.participants), strfmoney(event.expense_sum), strfmoney(event.expense_per_participant)])
    
    def update(self):
        self.update_events()
        self.update_expenses()

    
    def update_events(self, *indices):
        for index, row in enumerate(self.event_list):
            if len(indices) == 0 or index in indices:
                event_id = row[0]
                event = self.kasse.get_event(event_id)
                row[1] = event.name
                row[2] = len(event.participants)
                row[3] = strfmoney(event.expense_sum)
                row[4] = strfmoney(event.expense_per_participant)

    def update_expenses(self, *indices):
        for row in self.expense_list:
            if len(indices) == 0 or index in indices:
                expense = self.kasse.get_expense(row[0])
                row[1] = datetime.strftime(expense.date, datefmt)
                row[2] = "{:.2f} €".format(expense.amount / 100)
                row[3] = str(expense.description)

    def update_participations(self, *indices):
        for row in self.expense_list:
            if len(indices) == 0 or index in indices:
                expense = self.kasse.get_expense(row[0])
                row[1] = datetime.strftime(expense.date, datefmt)
                row[2] = "{:.2f} €".format(expense.amount / 100)
                row[3] = str(expense.description)

    def event_selected(self, selection):
        model, index = selection.get_selected()
        event_name = model[index][1]
        event = self.kasse.event_dict[event_name]
        self.event = event


        self.participants.clear()
        for person in self.kasse.persons:
            self.participants.append([person.id, person.name, person in event.participants])

        self.expense_list.clear()
        for expense in event.expenses:
            self.expense_list.append([expense.id, datetime.strftime(expense.date, datefmt), "{:.2f} €".format(expense.amount / 100), str(expense.description)])

    def participation_toggled(self, cell, index):
        person = self.kasse.get_person(self.participants[index][0])
        participate = not self.participants[index][2]
        self.participants[index][2] = participate
        if participate:
            self.kasse.participate(person, self.event)
        else:
            self.kasse.dont_participate(person, self.event)

        self.update()

    def on_event_name_changed(self, cell, index, new_value):
        event_id = self.event_list[index][0]
        event = self.kasse.get_event(event_id)
        event.name = new_value
        self.kasse.db.commit()
        self.event_list[index][1] = new_value


class GruppenkasseGui(object):
    glade_file = "./res/gruppenkasse.glade"
    def __init__(self, kasse):
        self.kasse = kasse
        self.builder = BuilderWrapper()
        self.builder.add_from_file(GruppenkasseGui.glade_file)

        self.event_tab = EventTab(self, self.kasse)
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
        self.kasse.close()
        Gtk.main_quit(*args)


class BuilderWrapper(Gtk.Builder):
    """ Mimics a Python dict to access the widgets in a syntatic sugared way """
    def __getitem__(self, key):
        return self.get_object(key)
        
