# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# TODO: search for WorksheetInterpreter subclasses inside the module
from .organizacoes import OrganizacoesInterpreter
from .recursos import RecursosInterpreter

INTERPRETERS = [OrganizacoesInterpreter, RecursosInterpreter]


class InterpreterFactory():
    @staticmethod
    def make_interpreter(importsheet, worksheet_title):
        '''Returns an interpreter for the given gspread worksheet.'''
        for interpreter_class in INTERPRETERS:
            if interpreter_class.worksheet_name == worksheet_title:
                worksheet = importsheet.spreadsheet.worksheet(worksheet_title)
                return interpreter_class(importsheet, worksheet)
        raise InterpreterNotFound(worksheet_title)


class InterpreterNotFound(Exception):
    def __init__(self, worksheet_name):
        self.worksheet_name = worksheet_name

    def __str__(self):
        return "Worksheet name '%s' is not recognized by any of the interpreters." % self.worksheet_name
