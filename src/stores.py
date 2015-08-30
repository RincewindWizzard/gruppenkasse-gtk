#!/usr/bin/python3
# -*- encoding: utf-8 -*-
from gi.repository import Gtk, GObject

#class ListStoreFilter(Gtk.ListStore):
#    def __init__(self, filter_func=None, modify_func=None, *args):

class CustomTreeModel(GObject.GObject, Gtk.TreeModel):
    def __init__(self, data):
        self.data = data
        self._num_rows = len(self.data)
        if self.data:
            self._n_columns = len(self.data[0])
        else:
            self._n_columns = 0
        GObject.GObject.__init__(self)

    def do_get_iter(self, path):
        """Returns a new TreeIter that points at path.
        The implementation returns a 2-tuple (bool, TreeIter|None).
        """
        indices = path.get_indices()
        if indices[0] < self._num_rows:
            iter_ = Gtk.TreeIter()
            iter_.user_data = indices[0]
            return (True, iter_)
        else:
            return (False, None)

    def do_iter_next(self, iter_):
        """Returns an iter pointing to the next column or None.
        The implementation returns a 2-tuple (bool, TreeIter|None).
        """
        if iter_.user_data is None and self._num_rows != 0:
            iter_.user_data = 0
            return (True, iter_)
        elif iter_.user_data < self._num_rows - 1:
            iter_.user_data += 1
            return (True, iter_)
        else:
            return (False, None)

    def do_iter_has_child(self, iter_):
        """True if iter has children."""
        return False

    def do_iter_nth_child(self, iter_, n):
        """Return iter that is set to the nth child of iter."""
        # We've got a flat list here, so iter_ is always None and the
        # nth child is the row.
        iter_ = Gtk.TreeIter()
        iter_.user_data = n
        return (True, iter_)

    def do_get_path(self, iter_):
        """Returns tree path references by iter."""
        if iter_.user_data is not None:
            path = Gtk.TreePath((iter_.user_data,))
            return path
        else:
            return None

    def do_get_value(self, iter_, column):
        """Returns the value for iter and column."""
        return str(self.data[iter_.user_data][column])

    def do_get_n_columns(self):
        """Returns the number of columns."""
        return self._n_columns

    def do_get_column_type(self, column):
        """Returns the type of the column."""
        # Here we only have strings.
        return str

    def do_get_flags(self):
        """Returns the flags supported by this interface."""
        return Gtk.TreeModelFlags.ITERS_PERSIST

class ListModifier(object):
    _singletons = {}
    """ Creates an altered view of a list """
    def __init__(self, data, col, value):
        self.data = data
        self.mapping = []

        # Filter all rows, which contain value in col
        for key, row in enumerate(data):
            if row[col] == value:
                self.mapping.append(key)

        self.col = col
        self.value = value

    def append(self, row):
        index = len(self.mapping)
        self.mapping.append(len(self.data))
        self.data.append(None)
        self[index] = row

    def __getitem__(self, key):
        row = tuple(self.data[self.mapping[key]])
        row = row[:self.col] + row[self.col + 1:]
        return row

    def __setitem__(self, key, row):
        row = tuple(row)
        row = tuple(row[:self.col] + (self.value,) + row[self.col + 1:])
        self.data[self.mapping[key]] = row

    def __delitem__(self, key):
        index = self.mapping[key]
        del self.data[index]
        del self.mapping[key]

    def __len__(self):
        return len(self.mapping)
