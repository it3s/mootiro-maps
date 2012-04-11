#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

import reversion
from lib.taggit.managers import TaggableManager


# class Grantor(models.Model):
#     """The giver part on an investment."""

#     name = models.CharField(max_length=256)
#     TYPE_CHOICES = (
#         ('P', _('Person')),
#         ('O', _('Organization')),
#     )
#     typ = models.CharField(verbose_name=_("type"), max_length=1, null=False,
#                             choices=TYPE_CHOICES)
#     is_anonymous = models.Boolean(default=False, null=False)

#     def __unicode__(self):
#         if self.is_anonymous:
#             return _("anonimous")
#         return unicode(self.name)


class Grantee(models.Model):
    """Abstract (but mapped to a table) class that works as proxy for the
    benefited part on a investment.
        Usage examples:
            investment.grantee = proposal
            investment.grantee = organization
            investment.grantee = resource
    """

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')


class Investment(models.Model):
    """A donation of money (or any other stuff) for either an Organization, a
    Proposal or a Resource in the system.
    """

    CURRENCIES_CHOICES = (
        ('BRL', _('Real')),
        ('USD', _('Dollar')),
        ('EUR', _('Euro')),
    )

    title = models.CharField(max_length=256)
    description = models.TextField()
    value = models.DecimalField(decimal_places=2, max_digits=14, null=True)
    currency = models.CharField(null=True, max_length=3, choices=CURRENCIES_CHOICES, default='BRL')

    date = models.DateField(null=False)
    over_period = models.BooleanField(default=False, null=False)
    end_date = models.DateField(null=True)

    # Meta info
    creator = models.ForeignKey(User, editable=False, null=True, blank=True,
                related_name='created_investments')
    creation_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    # Relationship
    _grantee = models.ForeignKey(Grantee, related_name="investments",
                    null=False, editable=False, blank=False)

    # Investment.grantee is a proxy for Grantee content_object
    @property
    def grantee(self):
        return self._grantee.content_object

    @grantee.setter
    def grantee(self, obj):
        self._grantee = Grantee(content_object=obj)

    tags = TaggableManager()

    def __unicode__(self):
        return unicode(self.title)

reversion.register(Investment)
