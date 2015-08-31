#!/usr/bin/python3
# -*- encoding: utf-8 -*-
from gi.repository import Gtk
from datetime import datetime

datefmt = '%d.%m.%y'

class BuilderWrapper(Gtk.Builder):
    """ Mimics a Python dict to access the widgets in a syntatic sugared way """
    def __getitem__(self, key):
        return self.get_object(key)

class Sidebar(object):
    def __init__(self, main_gui, kasse):
        self.kasse = kasse
        self.main_gui = main_gui

        builder = main_gui.builder

        self.person_listview = builder['person_list']
        self.event_listview = builder['event_list']

        self.person_list = Gtk.ListStore(str)
        self.event_list = Gtk.ListStore(str)

        self.person_listview.set_model(self.person_list)
        self.event_listview.set_model(self.event_list)

        self.person_listview.get_selection().connect('changed', self.person_selected)
        self.event_listview.get_selection().connect('changed', self.event_selected)

        self.update()

    def update(self):
        self.person_list.clear()
        self.event_list.clear()

        for person in self.kasse.persons:
            self.person_list.append([person.name])

        for event in self.kasse.events:
            self.event_list.append([event.name])

    def event_selected(self, selection):
        model, index = selection.get_selected()
        event_name = model[index][0]
        event = self.kasse.event_dict[event_name]
        self.main_gui.on_event_selected(event)

    def person_selected(self, selection):
        model, index = selection.get_selected()
        print(model[index][0])
        

class GruppenkasseGui(object):
    glade_file = "./res/gruppenkasse.glade"
    def __init__(self, model):
        self.model = model

        self.builder = BuilderWrapper()
        self.builder.add_from_file(GruppenkasseGui.glade_file)

        self.sidebar = Sidebar(self, self.model)
        self.builder["main_window"].show_all()

        #self.builder['person_list']

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
            expense_list.append([datetime.strftime(expense.date, datefmt), "{:.2f} €".format(expense.amount / 100), str(expense.description)])

        
