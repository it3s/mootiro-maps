#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django.db import models
from django.contrib.auth.models import User
import reversion
from need.models import Need


class Proposal(models.Model):
    """A proposed solution for solving a need"""

    class Meta:
        verbose_name = "solution proposal"
        verbose_name_plural = "solution proposals"

    title = models.CharField(max_length=256)
    description = models.TextField()
    number = models.IntegerField(null=False, editable=False)
    creation_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    # Relationships
    need = models.ForeignKey(Need, related_name='proposals')
    creator = models.ForeignKey(User, editable=False, null=True, blank=True,
                related_name='created_proposals')

    # Consummation, realization, attainment:
    realizers = models.ManyToManyField(User)
    # TODO: Also: organizations = model.ManyToManyField(Organization)
    cost = models.DecimalField(decimal_places=2, max_digits=14, null=True)
    report = models.TextField()

    def save(self, *args, **kwargs):
        if not self.id:
            # auto numbering a need's proposals
            self.number = Proposal.objects.filter(need=self.need).count() + 1
        super(Proposal, self).save(*args, **kwargs)

reversion.register(Proposal)
