#!/usr/bin/python3
# -*- encoding: utf-8 -*-
import sys, signal
from gui import GruppenkasseGui as GUI
from gui import DatabaseChooserDialog
from gi.repository import Gtk
from model import Gruppenkasse

signal.signal(signal.SIGINT, signal.SIG_DFL)

if __name__ == '__main__':
    database_path = None
    if len(sys.argv) >= 2:
        database_path = sys.argv[1]
    else:
        dialog = DatabaseChooserDialog()
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            database_path = dialog.get_filename()
        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")

        dialog.destroy()
        

    if database_path:
        kasse = Gruppenkasse(database_path)
        gui = GUI(kasse)
        gui.main()
