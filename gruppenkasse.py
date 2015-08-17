#!/usr/bin/python3
# -*- encoding: utf-8 -*-
import signal
from gi.repository import Gtk
import model

class GruppenkasseGUI(object):
    def __init__(self):
        # TODO: Load and Save Data
        # self.model = model.Fund
        import example_data
        self.model = example_data.kasse

        self.builder = builder = Gtk.Builder()
        self.builder.add_from_file("./res/gruppenkasse.glade")
        self.main_window = self.builder.get_object("main_window")

        # Navigation Sidebar
        self._selection_blocked = False # used for unselect_all
        self.person_list = Gtk.ListStore(str)
        self.builder.get_object("person_list").set_model(self.person_list)

        self.event_list = Gtk.ListStore(str)
        self.builder.get_object("event_list").set_model(self.event_list)
        self.update_view()

        # Connect all Signal handlers to this object
        self.builder.connect_signals(self)
        self.main_window.show_all()

    def update_view(self):
        """ Updates the Gui, so that it views the current state of the model """
        self.event_list.clear()
        self.person_list.clear()
        for person in self.model.persons:
            self.person_list.append([person.name])

        for event in self.model.events:
            self.event_list.append([event.name])

    # These two functions control the selection in the Navigation sidebar
    def on_person_selected(self, selection):
        if not self._selection_blocked:
            self._selection_blocked = True
            self.builder.get_object("event_list").get_selection().unselect_all()
            self._selection_blocked = False

            model, path = selection.get_selected_rows()
            print(model[path][0])

    def on_event_selected(self, selection):
        if not self._selection_blocked:
            self._selection_blocked = True
            self.builder.get_object("person_list").get_selection().unselect_all()
            self._selection_blocked = False

            model, path = selection.get_selected_rows()
            print(model[path][0])

    def on_add_event(self, *args):
        self.event_list.append(["Neue Veranstaltung"])

    def on_add_person(self, *args):
        self.person_list.append(["Neue Person"])

    def on_person_name_changed(self, cell, index, newname):
        self.person_list[index] = [newname]

    def on_event_name_changed(self, cell, index, newname):
        self.event_list[index] = [newname]

    def on_main_window_delete_event(self, *args):
        Gtk.main_quit(*args)

signal.signal(signal.SIGINT, signal.SIG_DFL)

if __name__ == "__main__":
    gui = GruppenkasseGUI()
    Gtk.main()
