# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from hashlib import sha1

from django.db import models
from django.core.urlresolvers import reverse

from django.contrib.auth.models import User

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

    @classmethod
    def calc_hash(self, s):
        # TODO: export this to config
        salt = 'batatinhaquandonasceespalharramapelochao'
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
        return reverse('user_profile', kwargs={'user_id': self.id})


class KomooProfile(GeoRefModel):
    # class KomooProfile(models.Model):
    user = models.OneToOneField(User)
    contact = models.TextField(null=True, blank=True)
    public_name = models.CharField(max_length=512, null=True, blank=True)

    def __repr__(self):
        return "<KomooProfile: {}>".format(unicode(self.user.username))

    def __unicode__(self):
        return self.name

    class Map:
        editable = False
        geometries = [POINT]
        categories = ['me', 'user']
        min_zoom_geometry = 0
        max_zoom_geometry = 100
        min_zoom_point = 100
        max_zoom_point = 100
        min_zoom_icon = 100
        max_zoom_icon = 100

    def files_set(self):
        """ pseudo-reverse query for retrieving Resource Files"""
        return UploadedFile.get_files_for(self)

    @property
    def view_url(self):
        return '/user/profile/%s/' % self.user.id

    @property
    def name(self):
        return self.public_name or self.user.username


# monkey patch auth.User \o/
# now we can retrieve a profile like: User.objects.get(pk=1).profile
User.profile = property(lambda u:
        KomooProfile.objects.get_or_create(user=u)[0])


def get_name(user):
    if user:
        name = ''
        if hasattr(user, 'profile') and user.profile:
            name = user.profile.public_name
        if not name:
            name = user.get_full_name()
        if not name:
            name = user.username
        return name
    else:
        return ''

def name(user):
    return get_name(user)

User.get_name = property(get_name)
User.name = property(name)
