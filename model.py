#!/usr/bin/python3
# -*- encoding: utf-8 -*-
from gi.repository import Gtk



def fill_store(store, data):
    """
    * Fills a store from a list of rows
    """
    for row in data:
        store.append(row if isinstance(row, tuple) else (row,))


# money transfer - date, person, amount, description
transfers = Gtk.ListStore(str, str, float, str)

# expenses of an event - date, event, amount, description
expenses = Gtk.ListStore(str, str, float, str)

# person names
persons = Gtk.ListStore(str)

# participations of person to events - event, person
participations = Gtk.ListStore(str, str)


