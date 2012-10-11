# -*- coding: utf-8 -*-

from komoo_user.models import KomooUser

from .models import ExternalCredentials


def encode_querystring(params):
    return '&'.join(['%s=%s' % (k, v) for k, v in params.items()])


def decode_querystring(s):
    return {p.split('=')[0]: p.split('=')[1] for p in s.split('&')}


def get_or_create_user_by_credentials(email, provider, access_data=None):
    '''
    Returns an user with the matching email if it exists, otherwise creates
    a new one with the e-mail already verified (user.is_active=True).
    '''
    user = None
    created = None
    provider_credentials = None

    matching_credentials = ExternalCredentials.objects.filter(email=email)
    for credential in matching_credentials:
        if not user:
            # any existing credential is already connected to a user
            user, created = credential.user, False
        if credential.provider == provider:
            provider_credentials = credential

    if not user:
        # first social login
        user, created = KomooUser.objects.get_or_create(email=email)
        user.is_active = True
        user.save()

    if not provider_credentials:
        # first login with this provider
        provider_credentials = ExternalCredentials(email=email,
                                                   provider=provider)
        provider_credentials.user = user
        # persist access_token and expiration date inside access_data
        provider_credentials.data = access_data
        provider_credentials.save()

    return user, created
