#!/usr/bin/python3
# -*- encoding: utf-8 -*-
import sys, signal
from gui import GruppenkasseGui as GUI
from model import Gruppenkasse

signal.signal(signal.SIGINT, signal.SIG_DFL)

if __name__ == '__main__':
    if len(sys.argv) > 2:
        database_path = sys.argv[1]
    else:
        database_path = sys.argv[1]
    kasse = Gruppenkasse(database_path)
    gui = GUI(kasse)
    gui.main()
