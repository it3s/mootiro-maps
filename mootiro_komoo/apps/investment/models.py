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

from main.utils import slugify


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
            investment.grantee = Grantee(proposal)
            investment.grantee = Grantee(organization)
            investment.grantee = Grantee(resource)
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
    # Auto-generated url slug. It's not editable via ModelForm.
    slug = models.CharField(max_length=256, null=False, blank=False, db_index=True, editable=False)
    description = models.TextField()
    value = models.DecimalField(decimal_places=2, max_digits=14, null=True, blank=True)
    currency = models.CharField(max_length=3, choices=CURRENCIES_CHOICES, null=True, blank=True)

    date = models.DateField(null=False)
    # TODO: remove over_period. Get this info by existence of an end_date
    over_period = models.BooleanField(default=False, null=False)
    end_date = models.DateField(null=True)

    # Meta info
    creator = models.ForeignKey(User, editable=False, null=False, blank=False,
                related_name='created_investments')
    creation_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    # Relationship
    grantee_content_type = models.ForeignKey(ContentType, editable=False)
    grantee_object_id = models.PositiveIntegerField(editable=False)
    grantee = generic.GenericForeignKey('grantee_content_type', 'grantee_object_id')

    # grantee_object = models.ForeignKey(Grantee, related_name="investments",
    #             null=False, editable=False, blank=False)

    # # Investment.grantee is a proxy for Grantee content_object
    # @property
    # def grantee(self):
    #     return self.grantee_object.content_object

    # @grantee.setter
    # def grantee(self, obj):
    #     self.grantee_object = Grantee(content_object=obj)

    tags = TaggableManager()

    def __unicode__(self):
        return unicode(self.title)

    ### Needed to slugify items ###
    def slug_exists(self, slug):
        """Answers if a given slug is valid in grantee investment namespace."""
        return Investment.objects.filter(slug=slug).exists()

    def save(self, *args, **kwargs):
        old_title = Investment.objects.get(id=self.id).title if self.id else None
        if not self.id or old_title != self.title:
            self.slug = slugify(self.title, self.slug_exists)
        super(Investment, self).save(*args, **kwargs)
    ### END ###

    def home_url():
        pass

    def home_url_params(self):
        d = dict(investment_slug=self.slug)
        d.update(self.grantee.home_url_params())
        return d

reversion.register(Investment)
