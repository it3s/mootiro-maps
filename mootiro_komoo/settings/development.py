# -*- coding: utf-8 -*-

'''Django settings for mootiro_komoo project

https://docs.djangoproject.com/en/dev/ref/settings/

Installation instructions:

   create a file named local_settings.py with your DB access info

This module imports everything from common.py, which is
under version control, and specializes it for development environment

'''

from __future__ import unicode_literals  # unicode by default
from common import *

DEBUG = True
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
# LANGUAGE_CODE = 'pt-br'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'ycx!))zk0_w(557x3rwvw)okxb^iai$ldtzno&pv*6^^iz1q=x'

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
            'level': 'DEBUG',
            'class': 'django.utils.log.NullHandler',
        },
        'log_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(SITE_ROOT, 'logs/log_dev.log'),
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'standard',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
        'request_handler': {
                'level': 'DEBUG',
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
           'level': 'DEBUG',
           'propagate': True
       },
    }
}
my_app_logger = {
    'handlers': ['console', 'log_file'],
    'level': 'DEBUG',
    'propagate': True
}
LOGGING['loggers'].update({'{}.views'.format(app): my_app_logger for app in os.listdir('apps/') + os.listdir('lib/')})
LOGGING['loggers'].update({'{}.models'.format(app): my_app_logger for app in os.listdir('apps/') + os.listdir('lib/')})
LOGGING['loggers'].update({'{}.forms'.format(app): my_app_logger for app in os.listdir('apps/') + os.listdir('lib/')})
LOGGING['loggers'].update({'{}.utils'.format(app): my_app_logger for app in os.listdir('apps/') + os.listdir('lib/')})


MIDDLEWARE_CLASSES += [
    'debug_toolbar.middleware.DebugToolbarMiddleware'
]

INSTALLED_APPS += [
    'debug_toolbar'
]

INTERNAL_IPS = ('127.0.0.1', )
DEBUG_TOOLBAR_CONFIG = {'INTERCEPT_REDIRECTS':  False}

# This for local_settings (user specific, like db access)
from local_settings import *
