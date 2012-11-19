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

from django.db import transaction
from projects.models import Project
from authentication.models import User
from importsheet.models import Importsheet
from organization.models import Organization

for org in Organization.objects.all():
    org.delete()

p = Project.objects.all()[0]
u = User.objects.all()[0]

l = Importsheet.objects.all()
ish = l[0] if l else \
                Importsheet(name='Mapeamento de Mapas', project=p, creator=u)
ish.save()
ret = ish.simulate('organization')
o = ret[0]['object']
# o.save()
