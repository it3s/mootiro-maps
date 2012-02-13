# -*- coding: utf-8 -*-

'''Django settings for mootiro_komoo project

This module imports everything from common.py, which is
under version control, and specializes it for production environment

'''

from __future__ import unicode_literals  # unicode by default
from common import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'mootiro_komoo',  # Or path to database file if using sqlite3.
        'USER': 'user',         # Not used with sqlite3.
        'PASSWORD': 'pass',   # Not used with sqlite3.
        'HOST': '',  # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',    # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = None  # 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'ycx!))zk0_w(557x3rwvw)okxb^iai$ldtzno&pv*6^^iz1q=x'

# production LOG goes here
