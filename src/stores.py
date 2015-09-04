#!/usr/bin/python3
# -*- encoding: utf-8 -*-
from gi.repository import Gtk, GObject
#class ListStoreFilter(Gtk.ListStore):
#    def __init__(self, filter_func=None, modify_func=None, *args):

class SQLStore(Gtk.ListStore):
    """
    Fills a Gtk.ListStore with data from a SQL query everytime you call update
    """

    def __init__(self, session, query, data_func, *types):
        """
        data_func(obj) is a function that takes an entry from the sql table an returns a tuple which has to contain the types given in types
        IMPORTANT: I implicit assume, that obj has an id entry of type int which is the full primary key of the row, which is added to the result of data_func and used to update the row in liststore
        """
        self._data_func = data_func
        self.session = session

        Gtk.ListStore.__init__(self, int, *types)
        self.query = query

    @property
    def query(self):
        return self._query

    @query.setter
    def query(self, q):
        self._query = q
        self.flush()

    @property
    def data_func(self):
        return self._data_func

    @data_func.setter
    def data_func(self, func):
        self._data_func = func
        self.flush()

    def flush(self):
        """ Clears all data and populates the store from the query """
        if self._data_func and self.query:
            self.clear()
            for obj in self.query.all():
                self.add_row(obj)

    def remove(self, index):
        row = self[index]
        self.query.filter_by(id=row[0]).delete() # deletes from undelying model
        self.session.commit()
        Gtk.ListStore.remove(self, index)

    def append_object(self, obj):
        self.session.add(obj)
        self.session.commit()
        index = self.add_row(obj)

        return index

    def add_row(self, obj):
        row = (obj.id, ) + self.data_func(obj)
        return self.append(row)

    def update_row(self, index):
        try:
            index = self.get_iter(index)
            if self.iter_is_valid(index):
                row = self[index]
                obj = self.query.filter_by(id=row[0]).first()
                if obj:
                    new_row = self.data_func(obj)
                    for j, val in enumerate(new_row):
                        row[j + 1] = val
                else:
                    self.remove(index)
        except ValueError as e:
            ...
            

    def update(self, *indices):
        if self._data_func and self.query:
            if len(indices) == 0:
                for index, row in enumerate(self):
                    self.update_row(index)

            else:
                for index in indices:
                    self.update_row(index)

    def get_object(self, index):
        row = self[index]
        return self.query.filter_by(id=row[0]).first()
    
