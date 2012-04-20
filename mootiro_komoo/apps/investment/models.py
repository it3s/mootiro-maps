# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.forms.models import model_to_dict

from annoying.functions import get_object_or_None

import reversion
from lib.taggit.managers import TaggableManager

from main.utils import slugify


class Investor(models.Model):
    """The giver part on an investment."""

    TYPE_CHOICES = (
        ('ORG', _('Organization')),
        ('PER', _('Person')),
    )

    anonymous_name = _("Anonymous")

    _name = models.CharField(max_length=256, null=True, blank=True)
    typ = models.CharField(max_length=3, null=False, choices=TYPE_CHOICES)
    is_anonymous = models.BooleanField(default=False, null=False)

    # Relationship
    content_type = models.ForeignKey(ContentType, editable=False, null=True)
    object_id = models.PositiveIntegerField(editable=False, null=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    @property
    def name(self):
        if self.is_anonymous:
            return unicode(self.anonymous_name)
        elif self.content_object:
            return unicode(self.content_object)
        else:
            return self._name

    @name.setter
    def name(self, value):
        if not self.content_object and not self.is_anonymous:
            self._name = value

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.is_anonymous or self.name == "":
            self.is_anonymous = True
            self.name = ""
        super(Investor, self).save(*args, **kwargs)

    @classmethod
    def get_or_create_for(cls, value):
        if isinstance(value, basestring):
            investor = cls(name=value)
            created = True
        else:
            investor = get_object_or_None(Investor, object_id=value.id,
                content_type=ContentType.objects.get_for_model(value))
            if not investor:
                investor = Investor()
                investor.content_object = value
                created = True
            else:
                created = False
        return investor, created


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

    # Relationships
    investor = models.ForeignKey(Investor, related_name="investments",
                    null=True, blank=True)

    # Grantee generic relationship
    grantee_content_type = models.ForeignKey(ContentType, editable=False,
                related_name="investment_grantee")
    grantee_object_id = models.PositiveIntegerField(editable=False)
    grantee = generic.GenericForeignKey('grantee_content_type', 'grantee_object_id')

    tags = TaggableManager()

    def __unicode__(self):
        return unicode(self.title)

    ### Needed to slugify items ###
    def slug_exists(self, slug):
        """Answers if a given slug is valid in grantee investment namespace."""
        return Investment.objects.filter(slug=slug).exists()

    def save(self, *args, **kwargs):
        # TODO: validate grantee as either a Proposal, a Resource or an Organization
        # TODO: validate investor as either a User or an Organization

        old_title = Investment.objects.get(id=self.id).title if self.id else None
        if not self.id or old_title != self.title:
            self.slug = slugify(self.title, self.slug_exists)
        super(Investment, self).save(*args, **kwargs)
    ### END ###

    def to_dict(self):
        fields = ["title", "description", "value", "currency", "date",
            "over_period", "end_date", "tags"]
        d = model_to_dict(self, fields=fields)
        if self.investor:
            d["investor_type"] = self.investor.typ
            d["anonymous_investor"] = self.investor.is_anonymous
            d["investor"] = self.investor.name
        return d

    def home_url():
        pass

    def home_url_params(self):
        d = dict(investment_slug=self.slug)
        d.update(self.grantee.home_url_params())
        return d

reversion.register(Investment)
