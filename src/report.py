#!/usr/bin/python3
# -*- encoding: utf-8 -*-
from datetime import datetime

def db_to_markdown(kasse):
    from gui import strfmoney, datefmt
    md =  "# Personen\n"
    for person in kasse.persons:
        md += "\n## {}\n".format(person.name)
        md += "{} hat {} eingezahlt. Davon wurden {} in Veranstaltungen investiert. Sein aktueller Kontostand ist {}.\n".format(person.name, strfmoney(person.payed), strfmoney(person.expenses), strfmoney(person.balance))
        md += "{} hat an folgenden Veranstaltungen teilgenommen:\n\n".format(person.name)
        for event in kasse.events:
            if person in event.participants:
                md += "* {}\n".format(event.name)

    md +=  "\n# Veranstaltungen\n"
    for event in kasse.events:
        md += "\n## {}\n".format(event.name)
        md += """Die Veranstaltung '{}' hat insgesamt {} gekostet. Verteilt auf {} Teilnehmer sind das {} pro Person.
Folgende Personen haben teilgenommen:\n\n""".format(event.name, strfmoney(event.expense_sum), len(event.participants), strfmoney(event.expense_per_participant))
        for person in event.participants:
            md += "* {}\n".format(person.name)

        md += "\nFolgende Kosten sind entstanden:\n\n"
        md += "| Datum | Betrag | Verwendungszweck |\n"
        md += "| --- | --- | --- |\n"
        for expense in event.expenses:
            md += "| {} | {} | {} |\n".format(datetime.strftime(expense.date, datefmt), strfmoney(expense.amount), expense.description)
    return md



    
