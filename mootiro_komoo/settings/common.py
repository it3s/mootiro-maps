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
ADMINS = ()
MANAGERS = ADMINS
SITE_ID = 1

# ========== Localization =====================================================
USE_I18N = True
USE_L10N = True
LOCALE_PATHS = (
    os.path.join(PROJECT_ROOT, 'locale'),
)

# ========== Static and Media =================================================
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media')
MEDIA_URL = '/media/'  # needs a trailing slash

STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')
STATIC_URL = '/static/'
STATICFILES_DIRS = ()

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
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_cas.middleware.CASMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'reversion.middleware.RevisionMiddleware',
    'mootiro_bar.DjangoMiddleware',
    'lib.mootiro_bar.DjangoMiddleware',
]

CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
)


TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)
TEMPLATE_DIRS = []
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
    'social_auth.backends.facebook.FacebookBackend',
    'social_auth.backends.google.GoogleOAuth2Backend',
    'django.contrib.auth.backends.ModelBackend',
    'user_cas.KomooCASBackend',  # http://code.google.com/p/django-cas/
)


# ========== Application ======================================================

LOGIN_URL = '/user/login'
AUTH_PROFILE_MODULE = 'user_cas.KomooProfile'

ROOT_URLCONF = 'mootiro_komoo.urls'

INSTALLED_APPS = [
    # django apps
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.comments',
    'django.contrib.gis',
    'django.contrib.markup',
    'django.contrib.humanize',

    # 3rd party apps
    'taggit',
    'django_js_utils',
    'crispy_forms',
    'reversion',
    'markitup',
    'lib.ajax_select',
    'fileupload',
    'gunicorn',
    'social_auth',
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
    'vote',
    'komoo_resource',
    'user_cas',
    'organization',
    'investment',
    'moderation',
    'hotsite',
    'signatures',
    'update',
    'komoo_project',
    'discussion',
]

COMMENT_MAX_LENGTH = 80 * 500  # ?? probably deprecated!
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024

# ==========  markiItUp =======================================================

MARKITUP_SET = 'markitup/sets/markdown_pt_BR'
MARKITUP_FILTER = ('main.utils.render_markup', {})
MARKITUP_AUTO_PREVIEW = True
JQUERY_URL = 'dummy.js'


# ========== Social Auth ======================================================
SOCIAL_AUTH_DEFAULT_USERNAME = 'mootiro_user'
SOCIAL_AUTH_UUID_LENGTH = 16
# SOCIAL_AUTH_EXPIRATION = 3600
SOCIAL_AUTH_SESSION_EXPIRATION = False
SOCIAL_AUTH_NEW_USER_REDIRECT_URL = '/'
# specific settings like tokens are on specialized settings


# ========== Komoo ============================================================
KOMOO_COMMENTS_WIDTH = 3
KOMOO_COMMENTS_HEIGHT = 20
KOMOO_DISABLE_MAP = False
DELETE_HOURS = 24
MOOTIRO_BAR_LOGIN_URL = '#'  # LOGIN_URL
MOOTIRO_BAR_LOGOUT_URL = '/user/logout'

# ========== Ajax-select ======================================================
AJAX_LOOKUP_CHANNELS = {
    'community': ('community.lookups', 'CommunityLookup'),
    'organizationcategory': ('organization.lookups',
                             'OrganizationCategoryLookup'),
    'user': ('user_cas.lookups', 'UserLookup'),
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

