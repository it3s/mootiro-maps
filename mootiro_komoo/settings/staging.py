# -*- coding: utf-8 -*-
from common import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.contrib.gis.db.backends.postgis',
#         'NAME': 'mootiro_komoo',
#         'USER': 'komoo_password_goes_here',
#         'PASSWORD': '',
#         'HOST': '',
#         'PORT': '',
#     }
# }

LANGUAGE_CODE = 'pt-br'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': '[%(levelname)s] [%(name)s:%(funcName)s] - %(asctime)s:'
                      '\n%(message)s'
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
            'filename': os.path.join(SITE_ROOT, 'logs/stage.log'),
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
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['request_handler', 'mail_admins'],
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
for mod in ['views', 'models', 'forms', 'utils']:
    LOGGING['loggers'].update({'{}.{}'.format(app, mod): my_app_logger
        for app in os.listdir('apps/')})

# user specific or secret settings
from local_settings import *

# ========= To override on local settings =====================================
# USER_PASSWORD_SALT = '...'
#
# BROKER_URL = "amqp://user:pass@localhost:5672/mootiro_maps_mq"
#
# FACEBOOK_APP_ID = '...'
# FACEBOOK_API_SECRET = '....'
# FACEBOOK_EXTENDED_PERMISSIONS = ['email']
#
# GOOGLE_OAUTH2_CLIENT_ID = '...'
# GOOGLE_OAUTH2_CLIENT_SECRET = '...'
#
# EMAIL_USE_TLS = True
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_HOST_USER = 'it3sdev@gmail.com'
# EMAIL_HOST_PASSWORD = '...'
#
# # the admin setting is necessary for sending mails when we have errors
# ADMINS =((,),)
#
# MAILGUN_API_KEY = "..."
