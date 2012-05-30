# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.core.urlresolvers import reverse
from django.db.models.signals import post_save

from annoying.functions import get_object_or_None

import reversion
from lib.taggit.managers import TaggableManager
from vote.models import VotableModel
from signatures.models import notify_on_update
from main.utils import slugify


class Investor(models.Model):
    """The giver part on an investment."""

    TYPE_CHOICES = (
        ('ORG', _('Organization')),
        ('PER', _('Person')),
    )

    @property
    def is_organization(self):
        return (self.typ == "ORG")

    @property
    def is_person(self):
        return (self.typ == "PER")

    # Fields
    anonymous_name = _("Anonymous")
    _name = models.CharField(max_length=256, null=True, blank=True)
    typ = models.CharField(max_length=3, null=False, blank=False, choices=TYPE_CHOICES)
    is_anonymous = models.BooleanField(default=False, null=False)

    # Generic Relationship
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

    def to_dict(self):
        d = {
            "investor_type": self.typ,
            "anonymous_investor": self.is_anonymous,
        }
        if self.is_organization:
            d["investor_organization"] = self.content_object.id
        elif self.is_person:
            d["investor_person"] = self.name
        return d

    @classmethod
    def get_or_create_for(cls, value, current=None):
        """Always ask this class method to build you a inventor based on what
        your investment already has."""
        if isinstance(value, basestring):
            if current:
                if current.name == value:
                    created = False
                    return current, created  # no changes
                else:
                    pass
                    current.investments.clear()
                    current.delete()  # new name
            investor = cls(name=value)
            investor.typ = "PER"
            created = True
        else:
            investor = get_object_or_None(Investor, object_id=value.id,
                content_type=ContentType.objects.get_for_model(value))
            if not investor:
                investor = Investor()
                investor.content_object = value
                # TODO: when add support to User must check content_object type
                #       before setting self typ below.
                investor.typ = "ORG"
                created = True
            else:
                created = False
        return investor, created

    @property
    def view_url(self):
        return self.content_object.view_url


class Investment(VotableModel):
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
    slug = models.CharField(max_length=256, null=False, blank=False,
                db_index=True, editable=False)
    description = models.TextField()
    value = models.DecimalField(decimal_places=2, max_digits=14, null=True,
                blank=True)
    currency = models.CharField(max_length=3, choices=CURRENCIES_CHOICES,
                null=True, blank=True)

    date = models.DateField(null=False)
    # TODO: remove over_period. Get this info by existence of an end_date
    over_period = models.BooleanField(default=False)
    end_date = models.DateField(null=True)

    # Meta info
    creator = models.ForeignKey(User, editable=False, null=True, blank=True,
                related_name='created_investments')
    creation_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    # Relationships
    investor = models.ForeignKey(Investor, related_name="investments",
                    null=True, blank=True)

    # Grantee generic relationship
    grantee_content_type = models.ForeignKey(ContentType, editable=False)
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

    # Url aliases
    @property
    def base_url_params(self):
        return self.grantee.home_url_params

    @property
    def home_url_params(self):
        d = self.base_url_params
        d.update(dict(investment_slug=self.slug))
        return d

    @property
    def view_url(self):
        return reverse('view_investment', kwargs=self.home_url_params)

    @property
    def edit_url(self):
        return reverse('edit_investment', kwargs=self.home_url_params)

reversion.register(Investment)

# connect follow notify signal
post_save.connect(notify_on_update, sender=Investment)
