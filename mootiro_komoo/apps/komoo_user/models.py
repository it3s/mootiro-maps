# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from hashlib import sha1

from django.conf import settings
from django.db import models
from django.core.urlresolvers import reverse

from fileupload.models import UploadedFile
from komoo_map.models import GeoRefModel, POINT


class KomooUser(GeoRefModel):
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
    def calc_hash(self, s):
        salt = settings.USER_PASSWORD_SALT
        return unicode(sha1(salt + s).hexdigest())

    def set_password(self, s):
        self.password = self.calc_hash(s)

    def verify_password(self, s):
        return self.password == self.calc_hash(s)

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
        return self.is_superuser()

    def has_module_perms(self, mod):
        return self.is_superuser()

    def has_perm(self, perm):
        return self.is_superuser()

