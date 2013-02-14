# -*- coding: utf-8 -*-
from common import *


SITE_URL = 'http://localhost:8001'
DEBUG = True
TEMPLATE_DEBUG = DEBUG
LANGUAGE_CODE = 'en-us'

SECRET_KEY = 'superawesomeninjapandasflyingintheskywithdoublerainbows'

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
            'level': 'DEBUG',
            'class': 'django.utils.log.NullHandler',
        },
        'log_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(SITE_ROOT, 'logs/dev.log'),
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
for mod in ['views', 'models', 'forms', 'utils']:
    LOGGING['loggers'].update({'{}.{}'.format(app, mod): my_app_logger
                    for app in os.listdir('apps/') + os.listdir('lib/')})

# Celery task queue config
BROKER_URL = "amqp://komoo:komoo@localhost:5672/mootiro_maps_mq"

# Development keys for external login providers
FACEBOOK_APP_ID = '186391648162058'
FACEBOOK_APP_SECRET = 'd6855cacdb51225519e8aa941cf7cfee'
GOOGLE_APP_ID = '66239815630.apps.googleusercontent.com'
GOOGLE_APP_SECRET = 'JNeq1VSkQzACfQ3yfNc5YYPL'

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'it3sdev@gmail.com'
EMAIL_HOST_PASSWORD = '...'  # password on local settings

ELASTICSEARCH_URL = '127.0.0.1:9200'
ELASTICSEARCH_INDEX_NAME = 'mootiro_maps_dev'

# user specific or secret settings
from local_settings import *

