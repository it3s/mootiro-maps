# -*- coding: utf-8 -*-
'''
This is script is an interactive way of exploring google spreadsheet API XMLs.
  To use it, do:

    fab shell
    run apps/importsheet/test

  ... inspect your variables. Good Luck! ...
'''
# from gdata.spreadsheets.client import SpreadsheetsClient
# from gdata.gauth import AuthSubToken

# import gspread
# from django.conf import settings

# skey = '0Ahdnyvg2LXX-dDFITkdXd0hBNFBDczA4RFV2dVBVM0E'
# gc = gspread.login(settings.IMPORTSHEET_GOOGLE_USER,
#                    settings.IMPORTSHEET_GOOGLE_PASSWORD)
# sh = gc.open_by_key(skey)
# worksheet = sh.worksheet('organization')

from projects.models import Project
from importsheet.models import Importsheet

p = Project.objects.all()[1]

print 1
ish = Importsheet(name='Uno', project=p)
print 2
ish.save()
print 3
ish = Importsheet(name='Duni', project=p)
print 4
ish.save()
print 5
