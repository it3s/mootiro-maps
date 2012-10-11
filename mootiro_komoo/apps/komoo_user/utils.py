# -*- coding: utf-8 -*-
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from .models import AnonymousUser
from .models import KomooUser as User


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
