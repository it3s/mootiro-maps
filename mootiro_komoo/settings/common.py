# -*- coding: utf-8 -*-
#
#  Global Settings
from __future__ import unicode_literals  # unicode by default
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_ROOT = os.path.dirname(PROJECT_ROOT)
APPS_ROOT = os.path.join(PROJECT_ROOT, 'apps')
LIB_ROOT = os.path.join(PROJECT_ROOT, 'lib')

# add folder to python path
sys.path.append(PROJECT_ROOT)
sys.path.append(APPS_ROOT)
sys.path.append(LIB_ROOT)

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

LOCALE_PATHS = (
    os.path.join(PROJECT_ROOT, 'locale'),
)

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

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

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'user_cas.KomooCASBackend',  # http://code.google.com/p/django-cas/
)
# Connect Mootiro Bar to django-cas:
LOGIN_URL = '/user/login'
MOOTIRO_BAR_LOGIN_URL = LOGIN_URL
MOOTIRO_BAR_LOGOUT_URL = '/user/logout'

DELETE_HOURS = 24

ROOT_URLCONF = 'mootiro_komoo.urls'

TEMPLATE_DIRS = [
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    # Nah. Walk SITE_ROOT looking for directories named "templates"?
    # SITE_ROOT + '/komoo/templates',

]

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
    # 3rd party apps
    'tinymce',
    'taggit',
    'django_js_utils',
    'crispy_forms',
    'reversion',
    'markitup',
    'lib.ajax_select',
    'fileupload',
    'gunicorn',
    # our apps
    'komoo_map',
    'community',
    'main',
    'need',
    'proposal',
    'komoo_comments',
    'vote',
    'komoo_resource',
    'user_cas',
    'organization',
    'investment',
    'moderation',
]

COMMENT_MAX_LENGTH = 80 * 500

# https://github.com/aljosa/django-tinymce/blob/master/docs/installation.rst
# TINYMCE_COMPRESSOR = True
TINYMCE_SPELLCHECKER = False
TINYMCE_DEFAULT_CONFIG = dict(
    plugins='table,paste,searchreplace,autolink',
    relative_urls=False,
    theme='advanced',
    cleanup_on_startup=True,
    # custom_undo_redo_levels=10,
    # content_css=,
    theme_advanced_toolbar_location="top",
    theme_advanced_statusbar_location='bottom',
    theme_advanced_resizing=True,
    # newdocument,|,justifyleft,justifycenter,justifyright,fontselect,fontsizeselect,forecolor,backcolor,|,cut,copy,paste,spellchecker,preview,|,advhr,emotions
    theme_advanced_buttons1="formatselect,bold,italic,underline,|,bullist,numlist,|,outdent,indent,|,removeformat",
    theme_advanced_buttons2="link,unlink,anchor,image,|,sub,sup,|,charmap,|,undo,redo,|,help,code,cleanup",
    theme_advanced_buttons3='',
)

# markiItUp
MARKITUP_SET = 'markitup/sets/markdown'
MARKITUP_FILTER = ('django.contrib.markup.templatetags.markup.markdown', {})
MARKITUP_AUTO_PREVIEW = True
JQUERY_URL = 'dummy.js'


#CAS config
PROFILE_DATABASE = 'localhost|profile|username|password'
CAS_SERVER_URL = 'https://localhost:8443/cas/'

# KOMOO Comments settings
KOMOO_COMMENTS_WIDTH = 3
KOMOO_COMMENTS_HEIGHT = 20

# AJAX-SELECT
# define the lookup channels in use on the site
AJAX_LOOKUP_CHANNELS = {
    #   pass a dict with the model and the field to search against
    'community': ('community.lookups', 'CommunityLookup'),
    'organizationcategory': ('organization.lookups', 'OrganizationCategoryLookup'),
}
# magically include jqueryUI/js/css
AJAX_SELECT_BOOTSTRAP = False
AJAX_SELECT_INLINES = False
