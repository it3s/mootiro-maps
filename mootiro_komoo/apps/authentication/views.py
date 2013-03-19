# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
import logging
from urllib import unquote

from django.shortcuts import redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import Http404
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext as _
from django.utils import simplejson
from django.forms.models import model_to_dict

from annoying.decorators import render_to, ajax_request

from signatures.models import Signature, DigestSignature
from ajaxforms import ajax_form
from main.utils import create_geojson, randstr, paginated_query
from main.tasks import send_explanations_mail, send_mail_async

from update.models import Update
from locker.models import Locker

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
        'komoo_resource.resource',
        'community.community',
        'organization.organization',
    ]
    weird_types = [
        'komoo_comments.comment',
    ]

    contrib = {}

    if data['model'] in regular_types + weird_types:
        if data['model'] in regular_types:
            obj = data['fields']
            contrib['id'] = version.object_id
            contrib['app_name'], contrib['model_name'] = data[
                    'model'].split('.')
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
                                    contrib['model_name'][0], contrib['id'])

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

    geojson = create_geojson([user], convert=False, discard_empty=True)
    if geojson:
        geojson['features'][0]['properties']['image'] = '/static/img/user.png'
        geojson = json.dumps(geojson)

    filters = request.GET.get('filters', [])
    if filters:
        filters = filters.split(',')
    if filters:
        query_set = Update.objects.filter(object_type__in=filters)
    else:
        query_set = Update.objects.all()

    reg = r'[^0-9]%d[^0-9]' % user.id
    query_set = query_set.filter(_user_ids__regex=reg).order_by('-date')
    updates_page = paginated_query(query_set, request, size=10)

    return dict(user_profile=user, geojson=geojson, updates_page=updates_page)


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

        user.save()

        user.send_confirmation_mail(request)
        send_explanations_mail(user)

        redirect_url = reverse('user_check_inbox')
        return {'redirect': redirect_url}

    return {'on_get': on_get, 'on_after_save': on_after_save}


@render_to('authentication/login.html')
def login(request):
    '''
    GET: Displays a page with login options.
    POST: Receives email and password and authenticate the user.
    '''
    if request.method == 'GET':
        next = request.GET.get('next', request.get_full_path())
        return dict(next=next)
    else:
        next = request.POST.get('next', request.get_full_path())

    if not next:
        next = '/'

    email = request.POST.get('email', '').lower()
    password = request.POST['password']
    if not email or not password:
        return dict(login_error='wrong_credentials', next=next)

    password = User.calc_hash(password)
    q = User.objects.filter(email=email, password=password)
    if not q.exists():
        return dict(login_error='wrong_credentials', next=next)

    user = q.get()
    if not user.is_active:
        return dict(login_error='user_not_active', next=next)

    auth_login(request, user)
    next = unquote(next)
    return redirect(next)


def logout(request):
    next_page = request.GET.get('next', '/')
    auth_logout(request)
    return redirect(next_page)


@render_to('authentication/explanations.org.html')
def explanations(request):
    name = request.GET.get('name', request.user.name)
    return {'name': name}


# =============================================================================


# @render_to('authentication/user_root.html')
# def user_root(request):
#         """
#         user_root is intended to only load a backbone router that
#         renders the diferent login/register pages
#         """
#         return {}


@render_to('authentication/verification.html')
def user_verification(request, key=''):
    '''
    Displays verification needed message if no key provided, or try to verify
    the user by the given key.
    '''
    # user_root_url = reverse('user_root')
    if not key:
        return {'message': 'check_email'}
    user_id = Locker.withdraw(key=key)
    user = User.get_by_id(user_id)
    if not user:
        # invalid key => invalid link
        raise Http404
    if not user.is_active:
        user.is_active = True
        user.save()
    return {'message': 'activated'}


# @render_to('global.html')
# def user_view(request, id_):
#     """
#     User page
#     """
#     user = request.user if id_ == 'me' else User.get_by_id(id_)
# 
#     if not user:
#         raise Http404
# 
#     user_data = user.to_cleaned_dict(user=request.user)
#     # filter data
#     return {
#                 'KomooNS_data': {
#                     'user': user_data
#                 }
#             }

