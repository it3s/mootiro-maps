# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
import logging

from django.shortcuts import redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import Http404
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext as _
from django.utils import simplejson
from django.forms.models import model_to_dict

from annoying.decorators import render_to, ajax_request
from annoying.functions import get_object_or_None
from reversion.models import Revision

from signatures.models import Signature, DigestSignature
from ajaxforms import ajax_form
from main.utils import create_geojson, randstr, send_mail

from .models import User
from .forms import FormProfile, FormUser
from .utils import login_required
from .utils import logout as auth_logout
from .utils import login as auth_login


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
        'resources.resource',
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
            ctype = ContentType.objects.get_for_id(
                            data['fields']['content_type'])
            obj = model_to_dict(ctype.get_object_for_this_type(
                    pk=data['fields']['object_id']))
            contrib['id'] = obj.get('id', '') or obj.get('pk', '')
            contrib['app_name'] = ctype.app_label
            contrib['model_name'] = ctype.name
            contrib['type'] = 'C'

        contrib['name'] = obj.get('name', '') or obj.get('title', '')
        contrib['date'] = created_date.strftime('%d/%m/%Y %H:%M')
        contrib['has_geojson'] = not 'EMPTY' in obj.get('geometry', 'EMPTY')
        contrib['permalink'] = "/permalink/{}{}".format(
                                    contrib['model_name'][0]
                if data['model'] != 'organization.organizationbranch' else 'o',
                contrib['id'])

    return contrib


@render_to('authentication/profile.html')
def profile(request, id=''):
    logger.debug('id : {}'.format(id))
    if not id:
        if request.user.is_authenticated():
            user = request.user
        else:
            return redirect(reverse('user_login'))
    else:
        user = get_object_or_404(User, id=id)
    contributions = []
    for rev in Revision.objects.filter(user=user
               ).order_by('-date_created')[:20]:
        version = rev.version_set.all()[0]
        contrib = _prepare_contrib_data(version, rev.date_created)
        if contrib:
            contributions.append(contrib)
    geojson = create_geojson([user], convert=False, discard_empty=True)
    if geojson:
        geojson['features'][0]['properties']['image'] = '/static/img/user.png'
        geojson = json.dumps(geojson)

    return dict(user_profile=user, contributions=contributions,
                geojson=geojson)


@render_to('authentication/profile_update.html')
@login_required
def profile_update(request):
    signatures = []
    for sig in Signature.objects.filter(user=request.user):
        try:
            ct = ContentType.objects.get_for_id(sig.content_type_id)
            obj = ct.get_object_for_this_type(pk=sig.object_id)

            signatures.append({
                'signature_id': sig.id,
                'obj_name': getattr(obj, 'name', '') or getattr(
                                    obj, 'title', ''),
                'obj_id': obj.id,
                'model_name': ct.name,
                'app_name': ct.app_label,
                'permalink': obj.view_url,
                'has_geojson': not 'EMPTY' in getattr(
                                    obj, 'geometry', 'EMPTY'),
            })
        except:
            # signature for an object that cannot be found (probably deleted)
            sig.delete()

    digest_obj = DigestSignature.objects.filter(user=request.user)
    digest = digest_obj[0].digest_type if digest_obj.count() \
                  else 'N'
    form_profile = FormProfile(instance=request.user)
    geojson = create_geojson([request.user], convert=False)
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
    logging.debug('POST: {}'.format(request.POST))
    # email = request.POST.get('email', '')
    current_password = request.POST.get('current_password', '')
    new_password = request.POST.get('password', '')
    confirm_password = request.POST.get('confirm_password', '')
    try:
        # if not email or email != request.user.email:
        #     return {
        #         'success': 'false',
        #         'errors': {
        #             'email': _('Email does not match with current user')}}
        if (not request.user.password or request.user.verify_password(
                                            current_password)):
            if not new_password:
                return {
                    'success': 'false',
                    'errors': {
                        'password': _('You must provide a valid password')}}
            if new_password != confirm_password:
                return {
                    'success': 'false',
                    'errors': {
                        'confirm_password': _('Passwords did not match')}}

            # current password verifies, has new password and
            # confirmation is equal,then saves new pass
            request.user.set_password(new_password)
            request.user.save()
            return {
                'success': 'true',
                'data': {}}

        else:
            # wrong pass (same as: has_passwd and not verify )
            return {
                    'success': 'false',
                    'errors': {
                        'current_password': _('Wrong password!')}}
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
        d = DigestSignature.objects.get(user=request.user)
        d.digest_type = 'N'
        d.save()
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


#
# ==================== Users ==================================================
#
@ajax_form('authentication/new.html', FormUser)
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
        while User.objects.filter(verification_key=key).exists():
            key = randstr(32)
        user.verification_key = key

        send_mail(
            title='Welcome to MootiroMaps',
            receivers=[user.email],
            message='''
Hello, {name}.

Before using our tool, please confirm your e-mail visiting the link below.
{verification_url}

Thanks,
the IT3S team.
'''.format(name=user.name, verification_url=request.build_absolute_uri(
                                reverse('user_verification', args=(key,))))
        )

        user.save()
        redirect_url = reverse('user_check_inbox')
        return {'redirect': redirect_url}

    return {'on_get': on_get, 'on_after_save': on_after_save}


@render_to('authentication/verification.html')
def user_verification(request, key=''):
    '''
    Displays verification needed message if no key provided, or try to verify
    the user by the given key.
    '''
    if not key:
        return dict(message='check_email')
    user = get_object_or_None(User, verification_key=key)
    if not user:
        # invalid key => invalid link
        raise Http404
    if user.is_active:
        return dict(message='already_verified')
    user.is_active = True
    user.save()
    return dict(message='activated')


@render_to('authentication/login.html')
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

    password = User.calc_hash(password)
    q = User.objects.filter(email=email, password=password)
    if not q.exists():
        return dict(login_error='wrong_credentials')

    user = q.get()
    if not user.is_active:
         return dict(login_error='user_not_active')

    auth_login(request, user)
    next = request.POST.get('next', '') or reverse('root')
    return redirect(next)


def logout(request):
    next_page = request.GET.get('next', '/')
    auth_logout(request)
    return redirect(next_page)

################ for testing ##################


@render_to('authentication/secret.html')
@login_required
def secret(request):
    return dict(user=request.user)


