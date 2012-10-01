#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
import logging
import requests

from django.shortcuts import redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext as _
from django.utils import simplejson
from django.forms.models import model_to_dict
from django.views.decorators.csrf import csrf_protect

from annoying.decorators import render_to, ajax_request
from annoying.functions import get_object_or_None
from reversion.models import Revision

from signatures.models import Signature, DigestSignature
from django_cas.views import _logout_url as cas_logout_url
from ajaxforms import ajax_form
from main.utils import create_geojson, randstr

from .forms import FormProfile, FormKomooUser, FormKomooUserLogin
from .models import KomooUser


logger = logging.getLogger(__name__)


def _prepare_contrib_data(version, created_date):
    """
    given a django-reversion.Version object we want a dict like:
    contrib = {
        id: object id (in case of comment, the referenced object id)
        name: presentation name
        model_name: name of the model
        app_name: name of the app (the django apps folder name)
        has_geojson: is it has or not a geojson
    }
    """
    data = simplejson.loads(version.serialized_data)[0]

    regular_types = [
        'need.need',
        'komoo_resource.resource',
        'community.community',
        'organization.organization',
        'organization.organizationbranch',
    ]
    weird_types = [
        'komoo_comments.comment',
    ]

    contrib = {}

    if data['model'] in regular_types + weird_types:
        if data['model'] in regular_types:
            obj = data['fields']
            contrib['id'] = version.object_id
            contrib['app_name'], contrib['model_name'] = data['model'].split('.')
            contrib['type'] = ['A', 'E', 'D'][version.type]

        elif data['model'] in weird_types:
            ctype = ContentType.objects.get_for_id(data['fields']['content_type'])
            obj = model_to_dict(ctype.get_object_for_this_type(
                    pk=data['fields']['object_id']))
            contrib['id'] = obj.get('id', '') or obj.get('pk', '')
            contrib['app_name'] = ctype.app_label
            contrib['model_name'] = ctype.name
            contrib['type'] = 'C'

        contrib['name'] = obj.get('name', '') or obj.get('title', '')
        contrib['date'] = created_date.strftime('%d/%m/%Y %H:%M')
        contrib['has_geojson'] = not 'EMPTY' in obj.get('geometry', 'EMPTY')
        contrib['permalink'] = "/permalink/{}{}".format(contrib['model_name'][0]
                if data['model'] != 'organization.organizationbranch' else 'o',
                contrib['id'])

    return contrib


@render_to('komoo_user/profile.html')
def profile(request, user_id=''):
    logger.debug('user_id : {}'.format(user_id))
    if not user_id:
        if request.user.is_authenticated():
            user = request.user
        else:
            return redirect(reverse('user_login'))
    else:
        user = get_object_or_404(User, id=user_id)
    contributions = []
    for rev in Revision.objects.filter(user=user
               ).order_by('-date_created')[:20]:
        version = rev.version_set.all()[0]
        contrib = _prepare_contrib_data(version, rev.date_created)
        if contrib:
            contributions.append(contrib)
    geojson = create_geojson([user.profile], convert=False, discard_empty=True)
    if geojson:
        geojson['features'][0]['properties']['image'] = '/static/img/user.png'
        geojson = json.dumps(geojson)
    return dict(user_profile=user, contributions=contributions, geojson=geojson)


@render_to('komoo_user/profile_update.html')
@login_required
def profile_update(request):
    signatures = []
    for sig in Signature.objects.filter(user=request.user):
        try:
            ct = ContentType.objects.get_for_id(sig.content_type_id)
            obj = ct.get_object_for_this_type(pk=sig.object_id)

            signatures.append({
                'signature_id': sig.id,
                'obj_name': getattr(obj, 'name', '') or getattr(obj, 'title', ''),
                'obj_id': obj.id,
                'model_name': ct.name,
                'app_name': ct.app_label,
                'permalink': '/permalink/{}{}'.format(ct.name[0], obj.id),
                'has_geojson': not 'EMPTY' in getattr(obj, 'geometry', 'EMPTY'),
            })
        except:
            #assinatura para um objeto que nao podeser encontrado
            sig.delete()

    digest_obj = DigestSignature.objects.filter(user=request.user)
    digest = digest_obj[0].digest_type if digest_obj.count() \
                  else ''
    form_profile = FormProfile(instance=request.user.profile)
    geojson = create_geojson([request.user.profile], convert=False)
    geojson['features'][0]['properties']['image'] = '/static/img/me.png'
    geojson = json.dumps(geojson)
    return dict(signatures=signatures, form_profile=form_profile,
                digest=digest, geojson=geojson)


@login_required
@ajax_form(form_class=FormProfile)
def profile_update_public_settings(request):
    return {}


@login_required
@ajax_request
def profile_update_personal_settings(request):
    # username = request.POST.get('username', '')
    try:
        # if not username:
        #     return dict(success='false',
        #                 errors={'username': _('Username Required')})

        # user_with_this_username = User.objects.filter(username=username)
        # if user_with_this_username.count():
        #     if user_with_this_username[0] != request.user:
        #         # same username , different users -> no no no
        #         return dict(success='false',
        #             errors={'username': _('This username already exists')})
        #     else:
        #         # same user, same username -> do nothing
        #         return dict(success='true', data={})
        # else:
        #     # new username =]
        #     request.user.username = username
        #     request.user.save()
            return dict(success='true', data={})
    except Exception as err:
        logger.error('OPS: ', err)
        return dict(success='false',
                    errors={"__all__": _('Failed to save data')})


@login_required
@ajax_request
def digest_update(request):
    logger.debug('POST: {}'.format(request.POST))
    digest_type = request.POST.get('digest_type', '')

    # update digest
    user_digest = DigestSignature.objects.filter(user=request.user)

    if digest_type and not user_digest.count():
        DigestSignature.objects.create(user=request.user,
                digest_type=digest_type)
    elif user_digest.count() and not digest_type:
        DigestSignature.objects.get(user=request.user).delete()
    elif user_digest.count() and digest_type != user_digest[0].digest_type:
        d = DigestSignature.objects.get(user=request.user)
        d.digest_type = digest_type
        d.save()

    return {'success': 'true'}


@login_required
@ajax_request
def signature_delete(request):
    id_ = request.POST.get('id', '')
    signature = get_object_or_404(Signature, pk=id_)
    if signature.user == request.user:
        signature.delete()
        return dict(success=True)
    return dict(success=False)


########## DJANGO USERS ##########
@ajax_form('komoo_user/new.html', FormKomooUser)
def user_new(request):
    '''Displays user creation form.'''

    def on_get(request, form):
        form.helper.form_action = reverse('user_new')
        return form

    def on_after_save(request, user):
        user.is_active = False
        user.set_password(request.POST['password'])

        # Email verification
        key = randstr(32)
        while KomooUser.objects.filter(verification_key=key).exists():
            key = randstr(32)
        user.verification_key = key
        # TODO: send email
        print '\n\nEMAIL USER VERIFICATION KEY\n%s\n\n' % user.verification_key

        user.save()
        redirect_url = reverse('user_check_inbox')
        return {'redirect': redirect_url}

    return {'on_get': on_get, 'on_after_save': on_after_save}


@render_to('komoo_user/verification.html')
def user_verification(request, key=''):
    '''
    Displays verification needed message if no key provided, or try to verify
    the user by the given key.
    '''
    if not key:
        return dict(message='check_email')
    user = get_object_or_None(KomooUser, verification_key=key)
    if not user:
        return dict(message='invalid_key')
    if user.is_active:
        return dict(message='already_verified')
    user.is_active = True
    user.save()
    return dict(message='activated')


@render_to('komoo_user/login.html')
def login(request):
    '''
    GET: Displays a page with login options.
    POST: Receives email and password and authenticate the user.
    '''

    if request.method == 'GET':
        next = request.GET.get('next', '')
        return dict(next=next)

    email = request.POST['email']
    password = request.POST['password']
    if not email or not password:
        return dict(login_error='wrong_credentials')

    password = KomooUser.calc_hash(password)
    q = KomooUser.objects.filter(email=email, _password=password)
    if not q.exists():
        return dict(login_error='wrong_credentials')

    user = q.get()
    if not user.is_active:
        return dict(login_error='user_not_active')

    _auth_login(request, user)

    next = request.POST.get('next', '') or reverse('root')
    return redirect(next)


def logout(request):
    next_page = request.GET.get('next', '/')
    auth_logout(request)
    # Is it the right thing to logout from SSO?
    # requests.get(cas_logout_url(request, next_page))
    return redirect(next_page)

##################################

def _auth_login(request, user):
    '''Persists user authentication in session.'''
    # Based in django.contrib.auth.login (auth_login)

    if 'user_id' in request.session:
        if request.session['user_id'] != user.id:
            # To avoid reusing another user's session, create a new, empty
            # session if the existing session corresponds to a different
            # authenticated user.
            request.session.flush()
    else:
        request.session.cycle_key()
    request.session['user_id'] = user.id
    request.user = user
