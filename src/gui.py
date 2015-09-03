#!/usr/bin/python3
# -*- encoding: utf-8 -*-
from gi.repository import Gtk
from datetime import datetime
from decimal import Decimal
from model import Person
from stores import SQLStore

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
        self.person_list = SQLStore(
            self.kasse.persons,
            lambda person: (person.name, strfmoney(person.payed), strfmoney(person.expenses), strfmoney(person.balance)),
            str, str, str, str
        )

        self.person_view = builder['person_list']
        self.person_view.set_model(self.person_list)
        self.person_view.get_selection().connect('changed', self.person_selected)

        self.remove_person_btn = builder['remove_person_btn']
        self.remove_person_btn.connect('clicked', self.on_remove_person)


        builder['add_person_btn'].connect('clicked', self.on_add_person)
        builder['person_cell'].connect('edited', self.person_name_changed)

        self.payments_list = SQLStore(
            None,
            lambda payment: (datetime.strftime(payment.date, datefmt), strfmoney(payment.amount), payment.description),
            str, str, str
        )

        self.update()

    def update(self):
        self.person_list.update()

    def person_selected(self, selection):
        model, index = selection.get_selected()
        if index and model.iter_is_valid(index):
            person_id = model[index][0]
            person = self.kasse.get_person(person_id)
            self.payments_list.query = self.kasse.payments.filter_by(person_id=person_id)
            self.remove_person_btn.set_sensitive(True)

    def on_add_person(self, btn):
        name = "Neue Person"
        number = 0
        while self.kasse.persons.filter_by(name="{} {}".format(name, number)).count() > 0:
            number += 1
        person = self.kasse.new_person("{} {}".format(name, number))
        self.kasse.db.commit()
        index = self.person_list.add_row(person)
        self.person_view.get_selection().select_iter(index)
        
    def on_remove_person(self, btn):
        store, index = self.person_view.get_selection().get_selected()
        row = store[index]
        self.kasse.persons.filter_by(id=row[0]).delete()
        self.person_list.update()
        self.person_view.get_selection().select_iter(self.person_list.get_iter_first())
        self.kasse.db.commit()

    def person_name_changed(self, cell, index, new_name):
        row = self.person_list[index]
        person = self.kasse.get_person(row[0])
        if person:
            person.name = new_name
            self.kasse.db.commit()
            self.person_list.update()






class EventTab(object):
    def __init__(self, main_gui, kasse):
        self.kasse = kasse
        self.main_gui = main_gui

        self.event = None

        self.event_list = SQLStore(
            self.kasse.events,
            lambda event: (event.name, len(event.participants), strfmoney(event.expense_sum), strfmoney(event.expense_per_participant)),
            str, int, str, str
        )

        self.expense_list = SQLStore(
            None,
            lambda expense: (datetime.strftime(expense.date, datefmt), "{:.2f} €".format(expense.amount / 100), str(expense.description)),
            str, str, str
        )

        self.participants_list = SQLStore(
            kasse.persons,
            lambda person: (person.name, person in self.event.participants if self.event else False),
            str, bool
        )

        builder = main_gui.builder

        self.event_listview = builder['event_list']
        self.event_listview.set_model(self.event_list)
        self.event_listview.get_selection().connect('changed', self.event_selected)

        root = self.event_list.get_iter_first()
        if root:
            self.event_listview.get_selection().select_iter(root)

        builder['participants_list'].set_model(self.participants_list)
        builder["expense_list"].set_model(self.expense_list)

        #self.participation_toggle =
        builder['participation_toggle'].connect("toggled", self.participation_toggled)
        builder['event_name_cell'].connect("edited", self.on_event_name_changed)

        #builder['add_expense'].connect("edited", self.on_add_expense)

    def update(self):
        self.event_list.update()
        self.expense_list.update()
        self.participants_list.update()

    def event_selected(self, selection):
        model, index = selection.get_selected()
        if index:
            event_name = model[index][1]
            event = self.kasse.event_dict[event_name]
            self.event = event
            self.update()

            self.expense_list.query = self.kasse.expenses.filter_by(event_id=event.id)

    def participation_toggled(self, cell, index):
        if self.event:
            row = self.participants_list[index]
            person = self.kasse.get_person(row[0])
            participate = not row[2]
            row[2] = participate

            
            if participate:
                self.kasse.participate(person, self.event)
            else:
                self.kasse.dont_participate(person, self.event)

            self.event_list.update()


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
        
