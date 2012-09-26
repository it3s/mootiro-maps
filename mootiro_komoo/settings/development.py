# -*- coding: utf-8 -*-
from common import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

TIME_ZONE = None
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
for mod in ['views', 'models', 'forms', 'utils']:
    LOGGING['loggers'].update({'{}.{}'.format(app, mod): my_app_logger
                    for app in os.listdir('apps/') + os.listdir('lib/')})

WANT_DEBUG_TOOLBAR = True

PROFILE_DATABASE = 'localhost|profile|username|password'
CAS_SERVER_URL = 'https://localhost:8443/cas/'

# Celery task queue config
BROKER_URL = "amqp://komoo:komoo@localhost:5672/mootiro_maps_mq"

FACEBOOK_APP_ID = '428903733789454'
FACEBOOK_API_SECRET = 'f286aad6b17af279e622d4350b077081'
FACEBOOK_EXTENDED_PERMISSIONS = ['email']

GOOGLE_OAUTH2_CLIENT_ID = '37410049822.apps.googleusercontent.com'
GOOGLE_OAUTH2_CLIENT_SECRET = 'VYPUXk4GraHit4n72nh5CwhX'

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'it3sdev@gmail.com'
EMAIL_HOST_PASSWORD = '...'  # password on local settings

# user specific or secret settings
from local_settings import *

if WANT_DEBUG_TOOLBAR:
    MIDDLEWARE_CLASSES += ['debug_toolbar.middleware.DebugToolbarMiddleware']
    INSTALLED_APPS += ['debug_toolbar']

    INTERNAL_IPS = ('127.0.0.1', )
    DEBUG_TOOLBAR_CONFIG = {'INTERCEPT_REDIRECTS': False}

