# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from hashlib import sha1

from django.db import models
from django.core.urlresolvers import reverse


from komoo_map.models import GeoRefModel


class KomooUser(GeoRefModel):

    # required info
    # username = models.CharField(max_length=256, null=False)
    name = models.CharField(max_length=256, null=False)
    email = models.CharField(max_length=512, null=False, unique=True)

    # password is set only if not created through external provider
    password = models.CharField(max_length=256, null=False)

    @classmethod
    def calc_hash(self, s):
        # TODO: export this to config
        salt = 'mateabesta'
        return unicode(sha1(salt + s).hexdigest())

    def set_password(self, s):
        self.password = self.calc_hash(s)

    def verify_password(self, s):
        return self.password == self.calc_hash(s)

    # other useful info to collect
    contact = models.TextField(null=True)

    # user management info
    is_active = models.BooleanField(default=False)
    verification_key = models.CharField(max_length=32, null=True)

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def __unicode__(self):
        return self.name

    @property
    def view_url(self):
        return reverse('user_profile', kwargs={'user_id': self.id})


