# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging
from urllib import unquote, quote

from django.shortcuts import redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext as _
from django.utils import translation
from django.conf import settings

from annoying.decorators import render_to, ajax_request

from signatures.models import Signature, DigestSignature
from ajaxforms import ajax_form
from main.utils import create_geojson, paginated_query, to_json
from main.tasks import send_explanations_mail

from update.models import Update
from locker.models import Locker

from .models import User
from .forms import FormProfile, FormUser
from .utils import login_required
from .utils import logout as auth_logout
from .utils import login as auth_login


logger = logging.getLogger(__name__)


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
        geojson = to_json(geojson)

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
    geojson = to_json(geojson)
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
                        'current_password': _('Wrong password')}}
    except Exception as err:
        logger.error('OPS: ', err)
        return dict(success='false',
                    errors={"__all__": _('Failed to save data')})


@login_required
def profile_update_language_settings(request):
    logging.debug('POST: {}'.format(request.POST))
    lang_code = request.POST.get('language', '')
    try:
        next_ = request.META.get('HTTP_REFERER', None)
        if not next_:
            next_ = '/'
        response = HttpResponseRedirect(next_)
        if lang_code and request.user.set_language(lang_code):
            # Save the user default language setting.
            request.user.save()
            # Update the session language.
            if hasattr(request, 'session'):
                request.session['django_language'] = lang_code
            else:
                response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code)
            translation.activate(lang_code)
    except Exception as err:
        logger.error('OPS: ', err)
    finally:
        return response


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


@ajax_form('authentication/login_and_new.html', FormUser)
def user_login_new(request):
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

    next = request.GET.get('next', request.get_full_path())
    return {'on_get': on_get, 'on_after_save': on_after_save, 'next': quote(next)}


@ajax_request
def test_email(request):
    user = request.user
    user.send_confirmation_mail(request)
    send_explanations_mail(user)
    return {'testing': '...'}


@render_to('authentication/login.html')
def login(request):
    '''
    GET: Displays a page with login options.
    POST: Receives email and password and authenticate the user.
    '''
    if request.method == 'GET':
        next = request.GET.get('next', request.get_full_path())
        return dict(next=quote(next))
    else:
        next = request.POST.get('next', request.get_full_path())

    if not next:
        next = '/'

    email = request.POST.get('email', '').lower()
    password = request.POST['password']
    if not email or not password:
        return dict(login_error='wrong_credentials', next=quote(next))

    password = User.calc_hash(password)
    q = User.objects.filter(email=email, password=password)
    if not q.exists():
        return dict(login_error='wrong_credentials', next=quote(next))

    user = q.get()
    if not user.is_active:
        return dict(login_error='user_not_active', next=quote(next))

    auth_login(request, user)
    next = unquote(next)
    response = HttpResponseRedirect(next)
    # Use language from user settings
    lang_code = user.language
    if lang_code and translation.check_for_language(lang_code):
        if hasattr(request, 'session'):
            request.session['django_language'] = lang_code
        else:
            response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code)
        translation.activate(lang_code)
    return response


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


@render_to('authentication/forgot_password.html')
def forgot_password(request):
    email_sent, error = False, ""
    if request.method == "POST":
        email = request.POST['email']
        user = User.objects.filter(email=email)
        user = user[0] if user.count() > 0 else None
        if user:
            user.send_recovery_mail(request)
            email_sent = True
        else:
            error = _('An error ocurred: E-mail not found on our database!')
    return {'email_sent': email_sent, 'error': error}


@render_to('authentication/recover_password.html')
def recover_password(request, key=''):
    if not key:
        return {'error': 'Invalid key, check your e-mail'}

    if request.method == "POST":
        if not request.POST['email']:
            return {'error': _('You must provide your e-mail')}

        if not request.POST['password']:
            return {'error': _('You must provide a password')}

        if request.POST["password"] != request.POST["password_confirmation"]:
            return {'error': _('Passwords do not match')}

        user_id = Locker.withdraw(key=key)
        user = User.get_by_id(user_id)

        if not user:
            # invalid key => invalid link
            return {'error': _('Invalid key')}

        if user.email != request.POST['email']:
            return {'error': _('User email and verification key do not match')}

        user.set_password(request.POST['password'])
        user.save()

        auth_login(request, user)
        response = HttpResponseRedirect('/')

        # Use language from user settings
        lang_code = user.language
        if lang_code and translation.check_for_language(lang_code):
            if hasattr(request, 'session'):
                request.session['django_language'] = lang_code
            else:
                response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code)
            translation.activate(lang_code)
        return response
    return {'key': key}


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

