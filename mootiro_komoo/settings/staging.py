# -*- coding: utf-8 -*-

'''
This module imports everything from common.py, which is
under version control, and specializes it for staging environment

'''

from __future__ import unicode_literals  # unicode by default
from common import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'mootiro_komoo',  # Or path to database file if using sqlite3.
        'USER': 'login',         # Not used with sqlite3.
        'PASSWORD': '',   # Not used with sqlite3.
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
LANGUAGE_CODE = 'pt-br'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'acwAJKSHKJSHKJS$%#%$#!!LKAJKSMLASMLMKAmkmlalkams'

# staging LOG goes here
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': '[%(levelname)s] [%(name)s : %(funcName)s] - %(asctime)s :\n%(message)s'
        },
    },
    'handlers': {
        'null': {
            'level': 'WARN',
            'class': 'django.utils.log.NullHandler',
        },
        'log_file': {
            'level': 'WARN',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(SITE_ROOT, 'logs/log_dev.log'),
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'standard',
        },
        'console': {
            'level': 'WARN',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
        'request_handler': {
                'level': 'WARN',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': os.path.join(SITE_ROOT, 'logs/django_request.log'),
                'maxBytes': 1024 * 1024 * 5,  # 5 MB
                'backupCount': 5,
                'formatter': 'standard',
        },
    },
    'loggers': {
#        'django': {
#            'handlers':['null'],
#            'propagate': True,
#            'level':'INFO',
#        },
        'django.request': {
            'handlers': ['request_handler'],
            'level': 'ERROR',
            'propagate': False
        },
        'django.db.backends': {
            'handlers': ['request_handler'],
            'level': 'ERROR',
            'propagate': False
        },
       'default': {
           'handlers': ['console', 'log_file'],
           'level': 'WARN',
           'propagate': True
       },
    }
}
my_app_logger = {
    'handlers': ['console', 'log_file'],
    'level': 'WARN',
    'propagate': True
}
LOGGING['loggers'].update({'{}.views'.format(app): my_app_logger for app in os.listdir('apps/')})
LOGGING['loggers'].update({'{}.models'.format(app): my_app_logger for app in os.listdir('apps/')})
LOGGING['loggers'].update({'{}.forms'.format(app): my_app_logger for app in os.listdir('apps/')})
LOGGING['loggers'].update({'{}.utils'.format(app): my_app_logger for app in os.listdir('apps/')})

#CAS config
PROFILE_DATABASE = 'localhost|mootiro_profile|mootiro_profile|.Pr0f1l3.'
CAS_SERVER_URL = 'https://login.mootiro.org/'
