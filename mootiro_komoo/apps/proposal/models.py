#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.contrib.contenttypes import generic

import reversion

from need.models import Need
from investment.models import Investment
from vote.models import VotableModel


class Proposal(VotableModel):
    """A proposed solution for solving a need"""

    class Meta:
        verbose_name = "solution proposal"
        verbose_name_plural = "solution proposals"

    title = models.CharField(max_length=256)
    description = models.TextField()
    number = models.IntegerField(null=False, blank=True, editable=False)
    creation_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    # Relationships
    need = models.ForeignKey(Need, related_name='proposals')
    creator = models.ForeignKey(User, editable=False, null=True, blank=True,
                related_name='created_proposals')

    # Consummation, realization, attainment:
    realizers = models.ManyToManyField(User)
    # TODO: Also: organizations = model.ManyToManyField(Organization)
    cost = models.DecimalField(decimal_places=2, max_digits=14, null=True, blank=True)
    report = models.TextField(null=True, blank=True)

    investments = generic.GenericRelation(Investment,
                        content_type_field='grantee_content_type',
                        object_id_field='grantee_object_id')

    @property
    def name(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.id:
            # auto numbering a need's proposals
            self.number = Proposal.objects.filter(need=self.need).count() + 1
        super(Proposal, self).save(*args, **kwargs)

    def __unicode__(self):
        return unicode(self.title)

    # Url aliases
    @property
    def base_url_params(self):
        return self.need.home_url_params

    @property
    def home_url_params(self):
        d = self.base_url_params
        d.update(dict(proposal_number=self.number))
        return d

    @property
    def view_url(self):
        return reverse('view_proposal', kwargs=self.home_url_params)

    @property
    def admin_url(self):
        return reverse('admin:{}_{}_change'.format(self._meta.app_label,
            self._meta.module_name), args=[self.id])

    @property
    def new_investment_url(self):
        return reverse('new_investment', kwargs=self.home_url_params)


if not reversion.is_registered(Need):
    reversion.register(Proposal)
