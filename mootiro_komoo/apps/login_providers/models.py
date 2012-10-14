# -*- coding: utf-8 -*-
from django.db import models
from jsonfield import JSONField

from komoo_user.models import User

PROVIDERS = {
    # 'provider label': 'db info'
    'facebook': 'facebook-oauth2',
    'google': 'google-oauth2',
    # 'twitter': 'twitter-oauth2',
}
PROVIDERS_CHOICES = [(t[1], t[0]) for t in PROVIDERS.items()]


class ExternalCredentials(models.Model):
    """
    User credentials for login on external authentication providers as Google,
    Facebook and Twitter.
    """

    user = models.ForeignKey(User)
    provider = models.CharField(max_length=32, choices=PROVIDERS_CHOICES)
    email = models.CharField(max_length=256)
    data = JSONField()  # provider specific data for user login
