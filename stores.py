#!/usr/bin/python3
# -*- encoding: utf-8 -*-
from gi.repository import Gtk
from gi.repository.GObject import GObject
from gi.repository import GObject as gobject
"""
* These are the models for the Treeviews
"""


def named_gobject(type_name, **properties):
    def __init__(self, **kwargs):
        GObject.__init__(self)
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __repr__(self):
        return "{}({})".format(
            type_name, 
            ", ".join([
                "{}={}".format(
                    k, 
                    repr(getattr(self, k))) 
                    for k, v in properties.items()
            ]))

    properties = { k: gobject.property(type=v) for k, v in properties.items()}
    return type(type_name, (GObject,), dict(__init__=__init__, __repr__=__repr__, **properties))
    


