# -*- coding: utf8 -*-
from __future__ import unicode_literals

# TODO: search for WorksheetInterpreter subclasses inside the module
from .organization import OrganizationInterpreter
INTERPRETERS = [OrganizationInterpreter]


class InterpreterFactory():
    @staticmethod
    def make_interpreter(worksheet):
        '''Returns an interpreter for the given gspread worksheet.'''
        for interpreter_class in INTERPRETERS:
            if interpreter_class.worksheet_name == worksheet.title:
                return interpreter_class(worksheet)
        raise InterpreterNotFound()


class InterpreterNotFound(Exception):
    def __str__(self):
        return 'Worksheet name is not recognized by any of the interpreters.'
