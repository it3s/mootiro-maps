# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from hashlib import sha1

from django.conf import settings
from django.db import models
from django.core.urlresolvers import reverse
from jsonfield import JSONField

from fileupload.models import UploadedFile
from komoo_map.models import GeoRefModel, POINT
from search.signals import index_object_for_search


class User(GeoRefModel):
    """
    User model. Replaces django.contrib.auth, CAS and social_auth
    with our own unified solution.
    its intended to use with external login providers.

    password: is set only if not created through external providers

    """
    name = models.CharField(max_length=256, null=False)
    email = models.CharField(max_length=512, null=False, unique=True)
    password = models.CharField(max_length=256, null=False)
    contact = models.TextField(null=True)

    creation_date = models.DateField(null=True, blank=True, auto_now_add=True)

    is_admin = models.BooleanField(default=False)

    # user management info
    is_active = models.BooleanField(default=False)
    verification_key = models.CharField(max_length=32, null=True)

    class Map:
        editable = False
        geometries = [POINT]
        categories = ['me', 'user']
        min_zoom_geometry = 0
        max_zoom_geometry = 100
        min_zoom_point = 100
        max_zoom_point = 100
        min_zoom_icon = 100
        max_zoom_icon = 10

    @classmethod
    def calc_hash(self, s, salt=None):
        if not salt:
            salt = settings.USER_PASSWORD_SALT
        return unicode(sha1(salt + s).hexdigest())

    def set_password(self, s):
        self.password = self.calc_hash(s)

    def verify_password(self, s, salt=None):
        return self.password == self.calc_hash(s, salt)

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def is_superuser(self):
        return self.is_admin

    def __unicode__(self):
        return unicode(self.name)

    @property
    def view_url(self):
        return reverse('user_profile', kwargs={'id': self.id})

    def files_set(self):
        """ pseudo-reverse query for retrieving Resource Files"""
        return UploadedFile.get_files_for(self)

    # The interface bellow is for django admin to work
    def is_staff(self):
        return self.is_admin

    def has_module_perms(self, mod):
        return self.is_admin

    def has_perm(self, perm):
        return self.is_admin

    def _social_auth_by_name(self, name):
        credentials = self.socialauth_set.all()
        l = filter(lambda s: s.provider == PROVIDERS[name], credentials)
        return l[0] if l else None

    def google(self):
        return self._social_auth_by_name('google')

    def facebook(self):
        return self._social_auth_by_name('facebook')

    def get_first_name(self):
        return self.name.split(' ')[0]

    def save(self, *args, **kwargs):
        r = super(User, self).save(*args, **kwargs)
        index_object_for_search.send(sender=self, obj=self)
        return r


class AnonymousUser(object):
    '''Dummy Class to integrate with other django apps.'''
    def is_authenticated(self):
        return False

    def is_anonymous(self):
        return True

    def is_superuser(self):
        return self.is_admin

    def is_admin(self):
        return False

    id = None


PROVIDERS = {
    # 'provider label': 'db info'
    'facebook': 'facebook-oauth2',
    'google': 'google-oauth2',
    # 'twitter': 'twitter-oauth2',
}
PROVIDERS_CHOICES = [(t[1], t[0]) for t in PROVIDERS.items()]


class SocialAuth(models.Model):
    """
    User credentials for login on external authentication providers as Google,
    Facebook and Twitter.
    """

    user = models.ForeignKey(User)
    provider = models.CharField(max_length=32, choices=PROVIDERS_CHOICES)
    email = models.CharField(max_length=256)
    data = JSONField()  # provider specific data for user login
