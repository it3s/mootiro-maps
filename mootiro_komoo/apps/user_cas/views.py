#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging
import requests

from django.shortcuts import redirect, get_object_or_404
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.utils import simplejson
from django.forms.models import model_to_dict

from annoying.decorators import render_to, ajax_request
from reversion.models import Revision

from main.utils import create_geojson
from signatures.models import Signature, DigestSignature
from django_cas.views import _logout_url as cas_logout_url
from ajaxforms import ajax_form

from .forms import FormProfile


logger = logging.getLogger(__name__)


#TODO: the function login should process the endpoint /login/cas/
#      And the endpoint /login/ should point to a new page that
#      matches our login design
def login(request):
    '''
    When the user clicks "login" on Mootiro Bar, this view runs.
    It redirects the user to CAS.
    '''
    logger.debug('accessing user_cas > login')
    host_port = request.environ['HTTP_HOST']
    return redirect(settings.CAS_SERVER_URL +
        '?service=http://{}/user/after_login'.format(host_port))


def logout(request):
    logger.debug('accessing user_cas > logout')
    next_page = request.GET.get('next', '/')
    auth_logout(request)
    requests.get(cas_logout_url(request, next_page))
    return redirect(next_page)


def _prepare_contrib_data(version, created_date):
    """
    given a django-reversion.Version object we want a dict like:
    contrib = {
        id: object id (in case of comment, the referenced object id)
        name: presentation name
        model_name: name of the model (used for retrieve proper image, in case on organization branch use ogranization)
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

    if data['model'] in regular_types:
        obj = data['fields']
        contrib['id'] = version.object_id
        contrib['name'] = obj.get('name', '') or obj.get('title', '')
        contrib['app_name'], contrib['model_name'] = data['model'].split('.')
        contrib['type'] = ['A', 'E', 'D'][version.type]
        contrib['has_geojson'] = not 'EMPTY' in obj.get('geometry', 'EMPTY')
        contrib['date'] = created_date.strftime('%d/%m/%Y %H:%M')

    elif data['model'] in weird_types:
        ctype = ContentType.objects.get_for_id(data['fields']['content_type'])
        obj = model_to_dict(ctype.get_object_for_this_type(
                pk=data['fields']['object_id']))
        contrib['id'] = obj.get( 'id', '' ) or obj.get( 'pk', '' )
        contrib['name'] = obj.get('name', '') or obj.get('title', '')
        contrib['app_name'], contrib['model_name'] = ctype.app_label, ctype.name 
        contrib['type'] = 'C'
        contrib['has_geojson'] = not 'EMPTY' in obj.get('geometry', 'EMPTY')
        contrib['date'] = created_date.strftime('%d/%m/%Y %H:%M')

    contrib['permalink'] = "/permalink/{}{}".format(contrib['model_name'][0] \
            if data['model'] != 'organization.organizationbranch' else 'o',
            contrib['id'])

    return contrib


@render_to('user_cas/profile.html')
def profile(request, username=''):
    logger.debug('acessing user_cas > profile : {}'.format(username))
    user = get_object_or_404(User, username=username)
    contributions = []
    for rev in Revision.objects.filter(user=user).order_by('-date_created')[:20]:
        version = rev.version_set.all()[0]
        contrib = _prepare_contrib_data(version, rev.date_created)
        contributions.append(contrib)
    return dict(user_profile=user, contributions=contributions)


@render_to('user_cas/profile_update.html')
@login_required
def profile_update(request):
    logger.debug('accessing user_cas > profile')
    signatures = Signature.objects.filter(user=request.user)
    digest_obj = DigestSignature.objects.filter(user=request.user)
    digest = digest_obj[0].digest_type if digest_obj.count() \
                  else ''
    form_profile = FormProfile(instance=request.user.profile)
    return dict(signatures=signatures, digest=digest, form_profile=form_profile)


@login_required
@ajax_form(form_class=FormProfile)
def profile_update_public_settings(request):
    return {}


@login_required
@ajax_request
def profile_update_personal_settings(request):
    # TODO implement-me
    return {}


@login_required
@ajax_request
def profile_update_signatures(request):
    # TODO fix-me
    logger.debug('accessing user_cas > profile_update')
    logger.debug('POST: {}'.format(request.POST))

    user = request.user
    username = request.POST.get('username', '')
    signatures = request.POST.getlist('signatures')
    digest_type = request.POST.get('digest_type', '')

    success = True
    errors = {}

    # validations
    if not username:
        success = False
        errors['username'] = _('You must provide a username')
    if User.objects.filter(username=username).exclude(pk=user.id).count():
        success = False
        errors['username'] = _('This username already exists')

    if not errors and success:
        # save username
        user.username = username
        user.save()

        # update signatures
        signatures = map(int, signatures) if signatures else []
        for signature in Signature.objects.filter(user=request.user):
            if not signature.id in signatures:
                signature.delete()

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

        return {'success': 'true', 'redirect': reverse('user_profile')}

    return {'success': 'false', 'errors': errors}

