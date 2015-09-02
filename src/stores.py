#!/usr/bin/python3
# -*- encoding: utf-8 -*-
from gi.repository import Gtk, GObject
#class ListStoreFilter(Gtk.ListStore):
#    def __init__(self, filter_func=None, modify_func=None, *args):

class SQLStore(Gtk.ListStore):
    """
    Fills a Gtk.ListStore with data from a SQL query everytime you call update
    """

    def __init__(self, query, data_func, *types):
        """
        data_func(obj) is a function that takes an entry from the sql table an returns a tuple which has to contain the types given in types
        IMPORTANT: I implicit assume, that obj has an id entry of type int which is the full primary key of the row, which is added to the result of data_func and used to update the row in liststore
        """
        self._data_func = data_func

        Gtk.ListStore.__init__(self, *types)
        self.query = query

    @property
    def query(self):
        return self._query

    @query.setter
    def query(self, q):
        self._query = q
        self.populate()

    @property
    def data_func(self):
        return self._data_func

    @data_func.setter
    def data_func(self, func):
        self._data_func = func
        self.populate()

    def populate(self):
        """ Clears all data and populates the store from the query """
        if self._data_func and self.query:
            self.clear()
            for obj in self.query.all():
                self.__add_row(obj)

    def __add_row(self, obj):
        row = (obj.id, ) + self.data_func(obj)
        self.append(row)

    def update_row(self, row):
        new_row = self.data_func(self.query.filter_by(id=row[0]).first())
        for j, val in enumerate(new_row):
            row[j + 1] = val

    def update(self, *indices):
        if self._data_func and self.query:
            if len(indices) == 0:
                for row in self:
                    self.update_row(row)

            else:
                for index in indices:
                    self.update_row(self[index])
    
