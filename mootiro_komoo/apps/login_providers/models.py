# -*- coding: utf-8 -*-
from django.db import models
from jsonfield import JSONField  # TODO: add this dependency

from komoo_user.models import KomooUser

PROVIDERS = (
    ('google-oauth2', 'google-oauth2'),
    ('facebook-oauth2', 'facebook-oauth2'),
    ('twitter-oauth', 'twitter-oauth'),
)

class ExternalCredentials(models.Model):
    '''
    User credentials for login on external authentication providers as Google,
    Facebook and Twitter.
    '''

    user = models.ForeignKey(KomooUser)
    provider = models.CharField(max_length=32, choices=PROVIDERS)
    email = models.CharField(max_length=256)
    data = JSONField()  # provider specific data for user login
