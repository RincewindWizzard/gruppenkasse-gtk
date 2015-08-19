#!/usr/bin/python3
# -*- encoding: utf-8 -*-
import signal
from gi.repository import Gtk
import model

class BuilderWrapper(Gtk.Builder):
    """ Mimics a Python dict to access the widgets in a syntatic sugared way """
    def __getitem__(self, key):
        return self.get_object(key)

class GruppenkasseGUI(object):
    def __init__(self):
        # TODO: Load and Save Data
        # self.model = model.Fund
        import example_data
        self.model = model.GruppenkasseStore()

        self.builder = BuilderWrapper()
        self.builder.add_from_file("./res/gruppenkasse.glade")
        self.main_window = self.builder["main_window"]

        # Navigation Sidebar
        self._selection_blocked = False # used for unselect_all
        self.builder.get_object("person_list").set_model(self.model.persons)
        column = self.builder["person_column"]
        column.set_sort_column_id(0)

        self.builder["event_list"].set_model(self.model.events)
        self.builder["event_column"].set_sort_column_id(0)

        # Connect all Signal handlers to this object
        self.builder.connect_signals(self)
        self.main_window.show_all()

    def unselect_sidebar(self, exclude):
        if not self._selection_blocked:
            self._selection_blocked = True
            for l in ["event_list", "person_list"]:
                selection = self.builder[l].get_selection()
                if not exclude == selection:
                    selection.unselect_all()

            self._selection_blocked = False

    # These two functions control the selection in the Navigation sidebar
    def on_person_selected(self, selection):
        if not self._selection_blocked:
            self.unselect_sidebar(exclude=selection)

            model, path = selection.get_selected_rows()
            person = model[path][0]

    def on_event_selected(self, selection):
        if not self._selection_blocked:
            self.unselect_sidebar(exclude=selection)

            model, path = selection.get_selected_rows()
            event = model[path][0]
            self.builder["participants_list"].set_model(self.model.participants_of(event))
            self.builder["expenses_list"].set_model(self.model.expenses_of(event))


    def on_participant_selected(self, selection):
        model, path = selection.get_selected_rows()


    def on_add_event(self, *args):
        self.builder["event_list"].get_model().append(["Neue Veranstaltung"])

    def on_add_person(self, *args):
        self.builder["person_list"].get_model().append(["Neue Person"])

    def on_person_name_changed(self, cell, index, newname):
        self.builder["person_list"].get_model()[index] = [newname]

    def on_event_name_changed(self, cell, index, newname):
        self.builder["event_list"].get_model()[index] = [newname]

    def on_main_window_delete_event(self, *args):
        Gtk.main_quit(*args)

signal.signal(signal.SIGINT, signal.SIG_DFL)

if __name__ == "__main__":
    gui = GruppenkasseGUI()
    Gtk.main()
