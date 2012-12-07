# -*- coding: utf-8 -*-
'''
This is script is an interactive way of exploring google spreadsheet API XMLs.
  To use it, do:

    fab shell
    run apps/importsheet/test

  ... inspect your variables. Good Luck! ...
'''

from importsheet.models import Importsheet

ish = Importsheet.objects.get(id=1)
ret = ish.insert('organization')
