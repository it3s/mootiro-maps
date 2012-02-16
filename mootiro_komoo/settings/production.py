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
            'level':'WARNING',
            'class':'django.utils.log.NullHandler',
        },
        'log_file': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(SITE_ROOT, 'logs/log_prod.log',
            'maxBytes': 1024*1024*50, # 5 MB
            'backupCount': 5,
            'formatter':'standard',
        },
        'console':{
            'level':'WARNING',
            'class':'logging.StreamHandler',
            'formatter': 'standard'
        },
        'request_handler': {
                'level':'WARNING',
                'class':'logging.handlers.RotatingFileHandler',
                'filename': os.path.join(SITE_ROOT, 'logs/django_request.log',
                'maxBytes': 1024*1024*50, # 5 MB
                'backupCount': 5,
                'formatter':'standard',
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
        'app': {
            'handlers': ['log_file'],
            'level': 'WARNING',
            'propagate': True
        },
    }
}
my_app_logger = {
    'handlers': ['log_file'],
    'level': 'WARNING',
    'propagate': True
}
LOGGING['loggers'].update({'{}.views'.format(app):my_app_logger for app in os.listdir('apps/')})
LOGGING['loggers'].update({'{}.models'.format(app):my_app_logger for app in os.listdir('apps/')})
LOGGING['loggers'].update({'{}.forms'.format(app):my_app_logger for app in os.listdir('apps/')})
LOGGING['loggers'].update({'{}.utils'.format(app):my_app_logger for app in os.listdir('apps/')})