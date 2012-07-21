#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default

import os
import urllib2
import json

import gettext

from genshi.template import TemplateLoader
from genshi.filters import Translator

# Import Pyramid dependencies
try:
    from pyramid.i18n import get_locale_name as pyramid_get_locale_name
except ImportError:
    pyramid_get_locale_name = None

# Import Django dependencies
try:
    from django.conf import settings as django_settings
    from django.utils import translation as django_translation
except ImportError:
    django_settings = None
    django_translation = None

DEFAULT_SERVICES = [
    ('Form', 'http://form.mootiro.org'),
    ('Vote', 'http://vote.mootiro.org'),
    ('Maps', 'http://maps.mootiro.org'),
    ('Wiki', 'http://wiki.mootiro.org'),
                    ]
DEFAULT_MAIN_LINK = ('Mootiro', 'http://mootiro.org')
# DEFAULT_USER_URL = '{}/user/profile'.format(DEFAULT_MAIN_LINK[1])
DEFAULT_USER_URL = '/user/profile/'
DEFAULT_LOGIN_URL = '/user/login'
DEFAULT_SETTINGS_URL = '/user/edit'
DEFAULT_LOGOUT_URL = '/user/logout'
DEFAULT_HELP_URL = '/help'

LOCAL_NOTIFICATIONS_PATH = '/mootiro_bar/notifications/'
REMOTE_NOTIFICATIONS_URLS = [
    'http://mootiro.org/service/notifications/user/{user}/{key}',
]

MOOTIRO_BAR_PLACEHOLDER = b'<!-- Mootiro_bar goes here -->'


# Load Mootiro Bar template
# To display changes in template file you should restart the server
_pkgpath = os.path.dirname(os.path.realpath(__file__))
_templates_path = os.path.join(_pkgpath, 'templates')
_template_loader = TemplateLoader(_templates_path, auto_reload=True)
template = _template_loader.load('mootiro_bar.html')

def get_alerts(user, key, locale='en'):
    """ Connect to remote location to get the 'user' notification.

    Return a tuple containing the content and the content_type.
    """
    # TODO: Maybe replace by connecting directly to databases
    content = '{}'
    content_type = ''
    if user is not None and hasattr('email', user) and user.email:
        url = REMOTE_NOTIFICATIONS_URLS[0].format(user=user.email, key=key)
        request = urllib2.Request(url)
        request.add_header('Cookie', '_LOCALE_={};'.format(locale))
        try:
            alerts_ = urllib2.urlopen(request)
            if alerts_.getcode() in (200, 301, 304, 307):
                content = alerts_.read()
                content_type = alerts_.info().type
            else:
                #TODO: raise an exception
                pass
        except urllib2.HTTPError as e:
            #TODO: raise an exception
            pass
    return content, content_type


def get_translations(locale='en'):
    try:
        translations = gettext.translation('mootiro_bar',
            os.path.join(os.path.dirname(os.path.realpath(__file__)),'locale'),
            [locale])
    except IOError:
        translations = gettext.translation('mootiro_bar',
            os.path.join(os.path.dirname(os.path.realpath(__file__)),'locale'),
            ['en'])
    finally:
        translations.install()
        return translations


def get_service_name_by_appname(appname):
    if appname == 'Mootiro Profile':
        return 'Mootiro'
    else:
        return appname.replace('Mootiro ', '')


def render(user=None, main_link=DEFAULT_MAIN_LINK, services=DEFAULT_SERVICES,
           urls=None, locale='en', selected=None, logout_method='GET'):
    """ Draw Mootiro Bar. """

    translations = get_translations(locale)

    # if urls is None:
    uname = user.username if user and hasattr(user, 'username') else ''
    urls = {'user': DEFAULT_USER_URL + uname,
            'login': DEFAULT_LOGIN_URL,
            'settings': DEFAULT_SETTINGS_URL,
            'logout': DEFAULT_LOGOUT_URL,
            'help': DEFAULT_HELP_URL}

    organizations_awaiting = []
    relationships_awaiting = []

    def elipsize(text, size=15):
        return text if size > len(text) else text[:13] + '…'

    show_nickname = user
    if user is not None:
        if hasattr(user, 'nickname'):
            show_nickname = elipsize(user.nickname)
        elif hasattr(user, 'username'):
            show_nickname = elipsize(user.username)
        elif hasattr(user, 'email'):
            username = user.email.split('@')[0]
            show_nickname = elipsize(username)

    return template.generate(user=show_nickname, enable_notifications=False,
        main_link=main_link, services=services, selected=selected,
        logout_method=logout_method, _=translations.ugettext,
        alerts_path=LOCAL_NOTIFICATIONS_PATH,
        user_url=urls.get('user', DEFAULT_USER_URL),
        login_url=urls.get('login', DEFAULT_LOGIN_URL),
        settings_url=urls.get('settings', DEFAULT_SETTINGS_URL),
        logout_url=urls.get('logout', DEFAULT_LOGOUT_URL),
        help_url=urls.get('help', DEFAULT_HELP_URL),
    ).render('html', encoding='ascii')


def mootiro_bar_tween_factory(handler, registry):
    """ Create a Pyramid Tween.

    To use it you need to edit your settings file to add the following text
    to [app:your_app] section:

        pyramid.tweens = mootiro_bar.mootiro_bar_tween_factory
                         pyramid.tweens.excview_tween_factory

    """
    settings = registry.settings

    def mootiro_bar_tween(request):
        """ Add the Mootiro Bar at the top of pyramid apps. """
        response = handler(request)
        # Intercept the request to LOCAL_NOTIFICATION_PATH to serve the
        # notifications json
        if request.path == LOCAL_NOTIFICATIONS_PATH:
            response.status_int = 200
            key = settings.get('alerts_url_key', '')
            response.body, response.content_type = get_alerts(user, key, locale)
            return response

        user = request.user
        locale = pyramid_get_locale_name(request)

        # Do nothing if the response content isn't html document or
        # response code isn't 200
        if not response.content_type.startswith('text/html') or \
                not response.status_int == 200:
            return response

        # Get some info from Pyramid app settings
        urls = {
            'user': settings.get('mootiro_bar.url.user', DEFAULT_USER_URL),
            'login': settings.get('mootiro_bar.url.login', DEFAULT_LOGIN_URL),
            'settings': settings.get('mootiro_bar.url.settings', DEFAULT_SETTINGS_URL),
            'logout': settings.get('mootiro_bar.url.logout', DEFAULT_LOGOUT_URL),
            'help': settings.get('mootiro_bar.url.help', DEFAULT_HELP_URL)
        }
        appname = settings.get('app.name', '')
        selected = settings.get('mootiro_bar.selected',
                                get_service_name_by_appname(appname))

        bar = render(user=user, urls=urls, locale=locale, selected=selected,
            logout_method=settings.get('mootiro_bar.logout_method', 'GET'))
        response.body = response.body.replace(MOOTIRO_BAR_PLACEHOLDER, bar)

        return response
    return mootiro_bar_tween


class DjangoMiddleware(object):
    """ Django Middleware.

    To use it you need to edit your settings file to add
    'mootiro_bar.DjangoMiddleware' to MIDDLEWARE_CLASSES list.
    """
    def process_response(self, request, response):
        settings = django_settings
        # Intercept the request to LOCAL_NOTIFICATION_PATH to serve the
        # notifications json
        if request.path == LOCAL_NOTIFICATIONS_PATH:
            key = getattr(settings, 'ALERTS_URL_KEY', '')
            response.content, content_type = get_alerts(user, key)
            response['Content-Type'] = content_type
            response['Content-Length'] = str(len(response.content))
            response.status_code = 200
            return response

        user = request.user if hasattr(request, 'user') \
                and request.user.is_authenticated() else None
        locale = getattr(settings, 'LANGUAGE_CODE', '')
        if not locale:
            locale = translation.get_language()
            # Fix the language string format
            if '-' in locale:
                locale = locale.replace('-', '_')
                locale = locale[:-2] + locale[:2].upper()

        request.environ['mootiro_bar.enabled'] = 'true'

        # Do nothing if the response content isn't html document or
        # response code isn't 200
        if not response['Content-Type'].startswith('text/html') or \
                not response.status_code == 200:
            return response

        # Get some info from Django app settings
        urls = {
            'user': getattr(settings, 'MOOTIRO_BAR_USER_URL', DEFAULT_USER_URL),
            'login': getattr(settings, 'MOOTIRO_BAR_LOGIN_URL', DEFAULT_LOGIN_URL),
            'settings': getattr(settings, 'MOOTIRO_BAR_SETTINGS_URL', DEFAULT_SETTINGS_URL),
            'logout': getattr(settings, 'MOOTIRO_BAR_LOGOUT_URL', DEFAULT_LOGOUT_URL),
            'help': getattr(settings, 'MOOTIRO_BAR_HELP_URL', DEFAULT_HELP_URL)
        }
        selected = getattr(settings, 'MOOTIRO_BAR_SELECTED', 'Maps')
        self.bar = render(user=user, urls=urls, locale=locale,
            selected=selected,
            logout_method=getattr(settings,
                'MOOTIRO_BAR_LOGOUT_METHOD', 'GET'),
        )
        response.content = response.content.replace(MOOTIRO_BAR_PLACEHOLDER, self.bar)
        response['Content-Length'] = str(len(response.content))
        return response


# TODO: need test
class SimpleWSGIMiddleware(object):
    """ Simple Middleware.

    Intercept the LOCAL_NOTIFICATIONS_PATH.
    """
    def __init__(self, application=None):
        self.application = application

    def __call__(self, environ, start_response):
        environ['mootiro_bar.enabled'] = 'true'

        def _start_response(code, headers):
            if request.path == LOCAL_NOTIFICATIONS_PATH:
                code = '200 OK'

            return start_response(code, headers)

        if request.path == LOCAL_NOTIFICATIONS_PATH:
            response = self.application(environ, _start_response)
            key = 'Change_me_to_a_random_string' #getattr(settings, 'alerts_url_key', '')
            content, content_type =  get_alerts(context.user, key)
            return content

        response = self.application(environ, _start_response)
        return response


# Pyramid Middleware (Deprecated)
class WSGIMiddleware(object):
    registry = False
    def __init__(self, application=None, selected=None, urls=None):
        self.application = application
        self.selected = selected
        self.urls = urls

    def __call__(self, environ, start_response):
        from pyramid.i18n import get_locale_name
        environ['mootiro_bar.enabled'] = 'true'
        global translations
        content_type = None
        content_length = None

        def _start_response(code, headers):
            from pyramid.threadlocal import get_current_registry
            # We will need the mootiro_web Registry instance to get some info
            # outside this  method.
            self.registry = get_current_registry()

            content_length = None
            content_type = None
            _headers = []
            # Gets the Content-Type and the Content-Length
            for h in headers:
                _h = h
                if h[0] == 'Content-Type':
                    content_type = h[1]
                if h[0] == 'Content-Length':
                    content_length = h[1]

                if not h[0] == 'Content-Length':
                    _headers.append(_h)

            # Uses the original header if we are not serving a html
            if not content_type or not content_type.startswith('text/html'):
                return start_response(code, headers)

            # Gets the pyramid request object
            request = self.application.request_factory(environ)

            if request.path == LOCAL_NOTIFICATIONS_PATH:
                code = '200 OK'

            # Gets the bar html code
            locale = get_locale_name(request)
            user = request.user
            self.user = user
            bar = render(user=user, urls=self.urls, locale=locale,
                logout_method=registry.settings.get \
                    ('mootiro_bar.logout_method', 'GET'))
            self.bar = bar

            if content_length:
                # Calculate the new Content-Length
                _h = ('Content-Length', str(int(content_length) + len(bar) - len(MOOTIRO_BAR_PLACEHOLDER)))
                _headers.append(_h)

            # Uses headers copy with new Content-Length
            return start_response(code, _headers)


        # Gets the pyramid request object
        request = self.application.request_factory(environ)

        if request.path == LOCAL_NOTIFICATIONS_PATH:
            response = self.application(environ, _start_response)
            key = getattr(settings, 'alerts_url_key', '')
            content, content_type =  get_alerts(request.user, key)
            return content

        # Avoid infinite loop
        if 'service/alerts' in request.url:
            response = self.application(environ, start_response)
        else:
            response = self.application(environ, _start_response)

        # Sets the registry instance we got at _start_response. This will be
        # internally needed by pyramid tho get current user.
        if self.registry:
            request.registry = self.registry

        def output():
            for s in response:
                if MOOTIRO_BAR_PLACEHOLDER in s:
                    user = request.user
                    # Gets the bar html code again only if needed
                    bar = self.bar if user == self.user else render( \
                        user=user, urls=self.urls,
                        locale=get_locale_name(request),
                        logout_method=registry.settings.get \
                            ('mootiro_bar.logout_method', 'GET')
                    )
                    yield s.replace(MOOTIRO_BAR_PLACEHOLDER, bar)
                else:
                    yield s

        return output()

