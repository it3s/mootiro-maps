# -*- coding: utf-8 -*-
import os
import sys
import djcelery

djcelery.setup_loader()

# ========== Path config ======================================================
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_ROOT = os.path.dirname(PROJECT_ROOT)
APPS_ROOT = os.path.join(PROJECT_ROOT, 'apps')
LIB_ROOT = os.path.join(PROJECT_ROOT, 'lib')

# add to python path
sys.path.append(PROJECT_ROOT)
sys.path.append(APPS_ROOT)
sys.path.append(LIB_ROOT)


# ========== admin, managers and site =========================================
ADMINS = (('it3sdev', 'it3sdev@gmail.com'),)
MANAGERS = ADMINS

# ========== Localization =====================================================
USE_I18N = True
USE_L10N = True
LOCALE_PATHS = (
    os.path.join(PROJECT_ROOT, 'locale'),
)
TIME_ZONE = 'America/Sao_Paulo'

# ========== Static and Media =================================================
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media')
MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(PROJECT_ROOT, 'public')
STATIC_URL = '/static/'
STATICFILES_DIRS = (os.path.join(PROJECT_ROOT, 'static'),)

ADMIN_MEDIA_PREFIX = '/static/admin/'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)


# ========== Middlewares, processors and loaders ==============================
MIDDLEWARE_CLASSES = [
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    # 'django.contrib.auth.middleware.AuthenticationMiddleware',
    'authentication.utils.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'lib.reversion.middleware.RevisionMiddleware',
]

CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
)


TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)
TEMPLATE_DIRS = (os.path.join(PROJECT_ROOT, 'templates'), )
TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.contrib.messages.context_processors.messages",
    "main.context_processors.social_keys",

)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)


# ========== Application ======================================================

ROOT_URLCONF = 'mootiro_komoo.urls'

INSTALLED_APPS = [
    # django apps
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.gis',
    'django.contrib.markup',
    'django.contrib.humanize',

    # 3rd party apps
    'taggit',
    'django_js_utils',
    'crispy_forms',
    'lib.reversion',
    'markitup',
    'lib.ajax_select',
    'fileupload',
    'gunicorn',
    'django_nose',
    'ajaxforms',
    'djcelery',

    # our apps
    'main',
    'komoo_map',
    'community',
    'need',
    'proposal',
    'komoo_comments',
    'komoo_resource',
    'authentication',
    'organization',
    'investment',
    'moderation',
    'hotsite',
    'signatures',
    'update',
    'komoo_project',
    'discussion',
    'importsheet',
]

FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024

# ========== markiItUp ========================================================

MARKITUP_SET = 'markitup/sets/markdown_pt_BR'
MARKITUP_FILTER = ('main.utils.render_markup', {})
MARKITUP_AUTO_PREVIEW = True
JQUERY_URL = 'dummy.js'

# ========== Komoo ============================================================
KOMOO_COMMENTS_WIDTH = 3
KOMOO_COMMENTS_HEIGHT = 20
KOMOO_DISABLE_MAP = False
DELETE_HOURS = 24

# ========== Importhseet ======================================================
IMPORTSHEET_SPREADSHEET_TEMPLATE_KEY = '0Ahdnyvg2LXX-dGotaTVzZFRicWJHbFFmSWJZSWF6OXc'
IMPORTSHEET_FUSION_TABLE_TEMPLATE_KEY = '1Ntfc5YPo5v62ytK2LE_vn2ZzqlUj_k1S4xWoBeI'

# ========== Ajax-select ======================================================
AJAX_LOOKUP_CHANNELS = {
    'community': ('community.lookups', 'CommunityLookup'),
    'organizationcategory': ('organization.lookups',
                             'OrganizationCategoryLookup'),
    'user': ('authentication.lookups', 'UserLookup'),
}
AJAX_SELECT_BOOTSTRAP = False
AJAX_SELECT_INLINES = False

# ========== Tests config =====================================================
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
NOSE_ARGS = ['--rednose', '--nocapture']
if 'test' in sys.argv:
    import logging
    logging.disable(logging.CRITICAL)
    FIXTURE_DIRS = ('fixtures/test/',)
    TESTING = True
else:
    TESTING = False

# ========== Mailgun ==========================================================
MAILGUN_API_URL = 'https://api.mailgun.net/v2/it3s.mailgun.org/messages'
MAILGUN_API_KEY = 'override me on local_settings'

