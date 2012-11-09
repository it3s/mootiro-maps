# -*- coding: utf-8 -*-
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from main.utils import send_mail

from .models import AnonymousUser
from .models import User, SocialAuth


class AuthenticationMiddleware(object):
    '''Middleware that appends the logged user to the request.'''

    def process_request(self, request):
        assert hasattr(request, 'session'), '''
            The authentication middleware requires session middleware to be
            installed. Edit your MIDDLEWARE_CLASSES setting to insert
            'django.contrib.sessions.middleware.SessionMiddleware'.'''

        if 'user_id' in request.session:
            try:
                request.user = User.objects.get(id=request.session['user_id'])
            except:
                request.session.pop('user_id')
                request.user = AnonymousUser()
        else:
            request.user = AnonymousUser()
        return None


# Code based in django.contrib.auth.login (auth_login)
def login(request, user):
    '''Persists user authentication in session.'''
    if 'user_id' in request.session:
        if request.session['user_id'] != user.id:
            # To avoid reusing another user's session, create a new, empty
            # session if the existing session corresponds to a different
            # authenticated user.
            request.session.flush()
    else:
        request.session.cycle_key()
    request.session['user_id'] = user.id


def logout(request):
    '''Drops session reference to the logged user.'''
    request.session.flush()
    if 'user_id' in request.session:
        request.session.pop('user_id')
    request.user = AnonymousUser()


def login_required(func=None):
    '''Decorator that requires a valid user in request.'''
    def wrapped_func(request, *a, **kw):
        if not request.user.is_authenticated():
            next = request.get_full_path()
            url = reverse('user_login') + '?next=' + next
            return redirect(url)
        else:
            return func(request, *a, **kw)
    return wrapped_func


def encode_querystring(params):
    return '&'.join(['%s=%s' % (k, v) for k, v in params.items()])


def decode_querystring(s):
    return {p.split('=')[0]: p.split('=')[1] for p in s.split('&')}


def get_or_create_user_by_credentials(email, provider, access_data=None):
    """
    Returns an user with the matching email if it exists, otherwise creates
    a new one with the e-mail already verified (user.is_active=True).
    """
    user = None
    created = None
    provider_credentials = None

    matching_credentials = SocialAuth.objects.filter(email=email)
    for credential in matching_credentials:
        if not user:
            # any existing credential is already connected to a user
            user, created = credential.user, False
        if credential.provider == provider:
            provider_credentials = credential

    if not user:
        # first social login
        user, created = User.objects.get_or_create(email=email)
        user.is_active = True
        user.save()

    if not provider_credentials:
        # first login with this provider
        provider_credentials = SocialAuth(email=email, provider=provider)
        provider_credentials.user = user
        # persist access_token and expiration date inside access_data
        provider_credentials.data = access_data
        provider_credentials.save()

    return user, created


def connect_or_merge_user_by_credentials(logged_user, email, provider):
    """
    Receives information about logged user and a social account to be connected
    (if not associated to any user) or merged into the logged user account
    information.
    """
    credentials = SocialAuth.objects.filter(email=email, provider=provider)

    if not credentials:
        credential = SocialAuth(email=email, provider=provider, user=logged_user)
        credential.save()
    else:
        credential = credentials[0]
        if credential.user == logged_user:
            return  # do nothing
        
        # merge users
        pass

