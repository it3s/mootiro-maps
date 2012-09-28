# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from fileupload.models import UploadedFile

from komoo_map.models import GeoRefModel, POINT


class KomooUser(GeoRefModel):

    # required info
    # username = models.CharField(max_length=256, null=False)
    name = models.CharField(max_length=256, null=False)
    email = models.CharField(max_length=512, null=False)
    
    # password is only if not created through external provider
    # TODO: encrypt password
    _password = models.CharField(max_length=256, null=False)

    def set_password(self, s):
        # TODO: use some hash solution
        self._password = s + 'hash'

    def verify_password(self, s):
        # TODO: use some hash solution
        return self._password == s + 'hash'

    # other useful info to collect
    contact = models.TextField(null=True)

    # user management info
    is_active = models.BooleanField(default=False)
    verification_key = models.CharField(max_length=32, null=True)

    def __repr__(self):
        return "<User: {}>".format(unicode(self.name))

    def __unicode__(self):
        return self.name

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
User.get_name = property(get_name)

