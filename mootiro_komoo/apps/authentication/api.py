# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _


from main.utils import (ResourceHandler, JsonResponse, JsonResponseNotFound,
        JsonResponseError, get_json_data, get_fields_to_show)
from main.datalog import log_data

from .models import User, Login
from .utils import login as auth_login
from .utils import logout as auth_logout


logger = logging.getLogger(__name__)


def _user_form_specific_validations(user, json_data, form_validates):
    """
    This method makes User's Form specific validation.
    Used on: /user <POST>
    """
    if not json_data.get('password_confirm', None):
        form_validates = False
        user.errors['password_confirm'] = _('Required field')

    license = json_data.get('license', '')
    license = True if license == 'agree' else False
    if not license:
        form_validates = False
        user.errors['license'] = _(''
            'You must accept the license agrement')
    if not json_data.get('password') == json_data.get('password_confirm'):
        form_validates = False
        user.errors['password_confirm'] = _(
                'Passwords did not match')
    return form_validates


class UserHandler(ResourceHandler):
    """ /users """

    def post(self, request):
        """
        Handles the RegisterForm from LoginView (authentication/views.coffee)
        Responsible for creating a new User account.
        """
        json_data = get_json_data(request)
        json_data['email'] = json_data.get('email', '').lower()
        user = User()
        user.from_dict(json_data)

        # user model validations
        form_validates = user.is_valid()
        form_validates = _user_form_specific_validations(
                user, json_data, form_validates)

        if not form_validates:
            return JsonResponseError(user.errors)
        else:
            user.is_active = False
            user.set_password(json_data.get('password'))
            user.save()
            user.send_confirmation_mail(request)
            return JsonResponse()


class UsersHandler(ResourceHandler):
    """ /users/[id_] """

    def get(self, request, id_):
        fields = get_fields_to_show(request,
                ['id', 'name', 'email', 'url', 'contact', 'about_me',
                 'is_admin'])
        user = request.user if id_ == 'me' else User.get_by_id(id_)

        if not user:
            return JsonResponseNotFound()

        user_data = user.to_cleaned_dict(fields=fields, user=request.user)
        return JsonResponse(user_data)

    def put(self, request, id_):
        """ Updates user data """

        json_data = get_json_data(request)
        user = User.get_by_id(id_)
        if not user:
            JsonResponseNotFound()

        if user.can_edit(request.user):
            user.from_dict(json_data)
            if not user.is_valid(ignore=['password']):
                return JsonResponseError(user.errors)

            user.save()
            log_data.send(
                    sender=user, object_=user, user=request.user, action='E')
            return JsonResponse({})
        else:
            return JsonResponseError({
                'all': _('You don\'t have permission for this operation')
            })


class UserUpdateHandler(ResourceHandler):
    """ /users/[id_]/update """

    def get(self, request, id_):
        # FIXME: Replace this fake implementation
        page = int(request.GET.get('page', 0))
        per_page = int(request.GET.get('per_page', ))
        return JsonResponse({
            'results': [
                {
                    'name': 'name {}'.format(page * per_page + i),
                    'id': page * per_page + i
                } for i in range(5)],
            'count': 25
        })


class LoginHandler(ResourceHandler):
    """ /users/login """

    def post(self, request):
        """
        Resposible for handle the LoginForm from LoginView
        (authentication/views.coffee)
        """
        json_data = get_json_data(request)
        email, password = [json_data.get(data, '')
                            for data in ['email', 'password']]
        email = email.lower()

        login = Login()
        login.from_dict({'email': email, 'password': password})
        if not login.is_valid():
            return JsonResponseError(login.errors, status_code=401)
        else:
            user = login.user
            auth_login(request, user)
            next_page = json_data.get('next', '') or reverse('root')
            if next_page.endswith('#'):
                next_page = next_page[:-1]
            return JsonResponse({'redirect': next_page})


class LogoutHandler(ResourceHandler):
    """ /users/logout """

    def get(self, request):
        next_page = request.GET.get('next', '') or reverse('root')
        if next_page.endswith('#'):
            next_page = next_page[:-1]
        auth_logout(request)
        print {'redirect': next_page}
        return JsonResponse({'redirect': next_page})
