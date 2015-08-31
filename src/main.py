#!/usr/bin/python3
# -*- encoding: utf-8 -*-
import sys, signal
from gui import GruppenkasseGui as GUI
from model import Gruppenkasse

signal.signal(signal.SIGINT, signal.SIG_DFL)

if __name__ == '__main__':
    database_path = sys.argv[1]
    kasse = Gruppenkasse(database_path)
    gui = GUI(kasse)
    gui.main()
