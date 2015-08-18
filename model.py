#!/usr/bin/python3
# -*- encoding: utf-8 -*-
from gi.repository import Gtk



def fill_store(store, data):
    """
    * Fills a store from a list of rows
    """
    for row in data:
        store.append(row if isinstance(row, tuple) else (row,))


class GruppenkasseStore(object):
    def __init__(self, transfers, expenses, persons, participations):
        # money transfer - date, person, amount, description
        self.transfers = Gtk.ListStore(str, str, float, str)
        fill_store(self.transfers, transfers)

        # expenses of an event - date, event, amount, description
        self.expenses = Gtk.ListStore(str, str, float, str)
        fill_store(self.expenses, expenses)

        # person names
        self.persons = Gtk.ListStore(str)
        fill_store(self.persons, persons)

        # participations of person to events - event, person
        self.participations = Gtk.ListStore(str, str)
        fill_store(self.participations, participations)

    def participants_of(self, event):
        """ 
        * Returns a liststore of all participants of an event
        """
        def visible_func(model, index, user_data):
            return model[index][0] == event

        modelfilter = self.participations.filter_new()
        modelfilter.set_visible_func(visible_func)

    def events_attended(self, person):
        """ 
        * Returns a liststore of all events this person attended
        """
        def visible_func(model, index, user_data):
            return model[index][0] == person

        modelfilter = self.participations.filter_new()
        modelfilter.set_visible_func(visible_func)        




