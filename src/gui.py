#!/usr/bin/python3
# -*- encoding: utf-8 -*-
from gi.repository import Gtk
from datetime import datetime
from decimal import Decimal
from model import Person, Event, Expense
from stores import SQLStore

datefmt = '%d.%m.%y'

def strfmoney(amount: "int cents"):
    return "{:.2f} €".format(amount / 100).replace(".", ",")

def strpmoney(amount):
    amount = amount.replace("€", "").replace(",", ".")
    return int(Decimal(amount) * 100)

# this function is used to render ints as money string
def money_cell_renderer(column, cell, store, index, user_data):
    return store[index]


class CRUD_TreeView(object):
    def __init__(self, store, treeview, add_btn, del_btn, select_func=None, create_func=None, modify_func=None, remove_func=None, changed_func=None):
        self.store = store
        self.treeview = treeview
        treeview.set_model(store)
        self.selection = treeview.get_selection()
        self.add_btn = add_btn
        self.del_btn = del_btn


        if not create_func:
            add_btn.set_sensitive(False)

        treeview.set_model(store)
        add_btn.connect('clicked', self.on_add_btn_clicked)
        del_btn.connect('clicked', self.on_del_btn_clicked)
        self.selection.connect('changed', self.on_selected)

        self.select_func = select_func
        self.create_func = create_func
        self.modify_func = modify_func
        self.remove_func = remove_func
        self.changed_func = changed_func

        for column in treeview.get_columns():
            for cell in column.get_cells():
                if cell.get_property("editable"):
                    cell.connect('edited', self.on_cell_modified, column)

    def get_selected_iter(self):
        _, index = self.selection.get_selected()
        return index
        

    def on_cell_modified(self, cell, index, new_value, column):
        obj = self.store.get_object(index)
    
        if obj and self.modify_func:
            self.modify_func(column, cell, index, obj, new_value)
            self.store.session.commit()
            self.store.update()
            self.changed_func()
        
    def on_add_btn_clicked(self, btn):
        obj = self.create_func()
        index = self.store.append_object(obj)
        self.selection.select_iter(index)
        self.changed_func()

    def on_selected(self, selection):
        self.del_btn.set_sensitive(True)
        index = self.get_selected_iter()
        if index:
            obj = self.store.get_object(index)
            if self.select_func:
                self.select_func(obj)

    def on_del_btn_clicked(self, btn):
        index = self.get_selected_iter()
        obj = self.store.get_object(index)
        next = self.store.iter_previous(index)

        if not self.remove_func or self.remove_func(obj):
            self.store.remove(index)

            if self.store.iter_is_valid(index):
                self.selection.select_iter(index)
            else:
                self.selection.select_iter(next)
            self.changed_func()
        


class PersonTab(object):
    def __init__(self, gui):
        self.kasse = gui.kasse
        builder = gui.builder
        self.person_list = SQLStore(
            self.kasse.db,
            self.kasse.persons,
            lambda person: (person.name, strfmoney(person.payed), strfmoney(person.expenses), strfmoney(person.balance)),
            str, str, str, str
        )

        self.person_view = builder['person_list']
        self.person_view.set_model(self.person_list)
        self.person_view.get_selection().connect('changed', self.person_selected)

        self.remove_person_btn = builder['remove_person_btn']
        self.remove_person_btn.connect('clicked', self.on_remove_person)


        builder['add_person_btn'].connect('clicked', self.on_add_person)
        builder['person_cell'].connect('edited', self.person_name_changed)

        self.payments_list = SQLStore(
            self.kasse.db,
            None,
            lambda payment: (datetime.strftime(payment.date, datefmt), strfmoney(payment.amount), payment.description),
            str, str, str
        )

        self.update()

    def update(self):
        self.person_list.update()

    def person_selected(self, selection):
        model, index = selection.get_selected()
        if index and model.iter_is_valid(index):
            person_id = model[index][0]
            person = self.kasse.get_person(person_id)
            self.payments_list.query = self.kasse.payments.filter_by(person_id=person_id)
            self.remove_person_btn.set_sensitive(True)

    def on_add_person(self, btn):
        name = "Neue Person"
        number = 0
        while self.kasse.persons.filter_by(name="{} {}".format(name, number)).count() > 0:
            number += 1
        person = self.kasse.new_person("{} {}".format(name, number))
        self.kasse.db.commit()
        index = self.person_list.add_row(person)
        self.person_view.get_selection().select_iter(index)
        
    def on_remove_person(self, btn):
        store, index = self.person_view.get_selection().get_selected()
        row = store[index]
        self.kasse.persons.filter_by(id=row[0]).delete()
        self.person_list.update()
        self.person_view.get_selection().select_iter(self.person_list.get_iter_first())
        self.kasse.db.commit()

    def person_name_changed(self, cell, index, new_name):
        row = self.person_list[index]
        person = self.kasse.get_person(row[0])
        if person:
            person.name = new_name
            self.kasse.db.commit()
            self.person_list.update()






class EventTab(object):
    def __init__(self, main_gui, kasse):
        self.kasse = kasse
        self.main_gui = main_gui

        self._event = None

        self.event_list = SQLStore(
            self.kasse.db,
            self.kasse.events,
            lambda event: (event.name, len(event.participants), strfmoney(event.expense_sum), strfmoney(event.expense_per_participant)),
            str, int, str, str
        )
        

        self.expense_list = SQLStore(
            self.kasse.db,
            None,
            lambda expense: (datetime.strftime(expense.date, datefmt), "{:.2f} €".format(expense.amount / 100), str(expense.description)),
            str, str, str
        )

        self.participants_list = SQLStore(
            self.kasse.db,
            kasse.persons,
            lambda person: (person.name, person in self.event.participants if self.event else False),
            str, bool
        )

        builder = main_gui.builder

        self.event_listview = builder['event_list']
        self.expense_listview = builder['expense_list']

        self.event_crud = CRUD_TreeView(
            self.event_list, 
            self.event_listview, 
            builder['add_event_btn'], 
            builder['remove_event_btn'], 
            select_func=self.on_event_selected, 
            create_func=self.on_create_event, 
            modify_func=self.on_edit_event,
            remove_func=self.on_remove_event
        )

        self.expense_crud = CRUD_TreeView(
            self.expense_list, 
            self.expense_listview, 
            builder['add_expense_btn'], 
            builder['remove_expense_btn'], 
            select_func=self.on_expense_selected, 
            create_func=self.on_create_expense, 
            modify_func=self.on_edit_expense,
            remove_func=self.on_remove_expense,
            changed_func=self.on_expenses_changed
        )

        root = self.event_list.get_iter_first()
        if root:
            self.event_listview.get_selection().select_iter(root)

        builder['participants_list'].set_model(self.participants_list)
        self.expense_listview.set_model(self.expense_list)

        #self.participation_toggle =
        builder['participation_toggle'].connect("toggled", self.participation_toggled)

        # cells that can be edited
        self.event_name_cell = builder['event_name_cell']
        self.expense_date_cell = builder['expense_date_cell']
        self.expense_amount_cell = builder['expense_amount_cell']
        self.expense_description_cell = builder['expense_description_cell']



        #builder['add_expense'].connect("edited", self.on_add_expense)

    # --------------------------------------------------------------------------
    # Event CRUD Listeners
    def on_event_selected(self, event):
        self.event = event

    def on_create_event(self):
        return self.kasse.new_event("Neue Veranstaltung")

    def on_edit_event(self, column, cell, index, obj, new_value):
        if cell == self.event_name_cell:
            obj.name = new_value

    def on_remove_event(self, event):
        # remove all participations and expenses
        self.kasse.remove_event(event)
        return True

    # --------------------------------------------------------------------------
    # expense CRUD Listeners
    def on_expense_selected(self, event):
        ...

    def on_create_expense(self):
        expense = Expense(date=datetime.now(), event=self.event, amount=0, description="")
        return expense

    def on_edit_expense(self, column, cell, index, expense, new_value):
        if cell == self.expense_date_cell:
            expense.date = datetime.strptime(new_value, datefmt)
        elif cell == self.expense_amount_cell:
            expense.amount = strpmoney(new_value)
        elif cell == self.expense_description_cell:
            expense.description = new_value
        

    def on_remove_expense(self, event):
        self.event_list.update()
        return True

    def on_expenses_changed(self):
        self.event_list.update()

    # ---------------------------------------------------------------------------

    @property
    def event(self):
        return self._event

    @event.setter
    def event(self, event):
        self._event = event
        if event:
            self.expense_list.query = self.kasse.db.query(Expense).filter_by(event_id=event.id)
            self.expense_crud.add_btn.set_sensitive(True)
        self.expense_list.update()
        self.participants_list.update()

    def update(self):
        self.event_list.update()
        self.expense_list.update()
        self.participants_list.update()

    def participation_toggled(self, cell, index):
        if self.event:
            row = self.participants_list[index]
            person = self.kasse.get_person(row[0])
            participate = not row[2]
            row[2] = participate

            
            if participate:
                self.kasse.participate(person, self.event)
            else:
                self.kasse.dont_participate(person, self.event)

            self.event_list.update()



class GruppenkasseGui(object):
    glade_file = "./res/gruppenkasse.glade"
    def __init__(self, kasse):
        self.kasse = kasse
        self.builder = BuilderWrapper()
        self.builder.add_from_file(GruppenkasseGui.glade_file)

        self.event_tab = EventTab(self, self.kasse)
        self.person_tab = PersonTab(self)

        self.builder["main_window"].show_all()

        self.builder['person_list']

        # delete Event
        self.builder['main_window'].connect("delete-event", self.on_main_window_delete_event)

    def main(self):
        Gtk.main()

    #---------------------------------------------------------------------------
    # Signals
    def on_main_window_delete_event(self, *args):
        self.kasse.close()
        Gtk.main_quit(*args)


class BuilderWrapper(Gtk.Builder):
    """ Mimics a Python dict to access the widgets in a syntatic sugared way """
    def __getitem__(self, key):
        return self.get_object(key)
        
