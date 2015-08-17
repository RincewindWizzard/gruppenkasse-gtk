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
    

if __name__ == "__main__":
    Person = named_gobject("Person", vorname=str, nachname=str, alter=int)
    p = Person(vorname="John", nachname="Smith", alter=42)
    p.friend = Person(vorname="Jack", nachname="Daniel", alter=18)
    print(p)
    print(p.friend)
