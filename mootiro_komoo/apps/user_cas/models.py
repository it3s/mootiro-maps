# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from fileupload.models import UploadedFile
from komoo_map.models import GeoRefModel


# class KomooProfile(GeoRefModel):
class KomooProfile(models.Model):
    user = models.OneToOneField(User)
    contact = models.TextField(null=True, blank=True)
    public_name = models.CharField(max_length=512, null=True, blank=True)

    def __unicode__(self):
        return "<KomooProfile: {}>".format(unicode(self.user.username))

    class Map:
        editable = False

    def files_set(self):
        """ pseudo-reverse query for retrieving Resource Files"""
        return UploadedFile.get_files_for(self)


# monkey patch auth.User \o/
# now we can retrieve a profile like: User.objects.get(pk=1).profile
User.profile = property(lambda u:
        KomooProfile.objects.get_or_create(user=u)[0])

