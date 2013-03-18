# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from main.views import ENTITY_MODEL


class HighlightSection(models.Model):
    PAGE_CHOICES = (
        ('/object', '/object'),
        ('/project', '/project'),
    )
    name = models.CharField(max_length=64, blank=False)
    icon_src = models.CharField(max_length=256, null=True, blank=True)
    
    page_name = models.CharField(max_length=32, null=False, blank=False, choices=PAGE_CHOICES)
    page_order = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=False)

    def __unicode__(self):
        return unicode("{} :: {}".format(self.page_name, self.name))

    def highlights(self):
        return self.highlight_set.filter(is_active=True).order_by('section_order')


class Highlight(models.Model):
    OBJECT_TYPE_CHOICES = [(k, cls.__name__) for k, cls in ENTITY_MODEL.items()]

    section = models.ForeignKey(HighlightSection, null=True, blank=True)
    
    name = models.CharField(max_length=64, blank=False)
    description = models.CharField(max_length=256, blank=False)
    object_type = models.CharField(max_length=1, blank=False, choices=OBJECT_TYPE_CHOICES)
    object_id = models.IntegerField(null=False)
    
    section_order = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=False)

    def __unicode__(self):
        return unicode("{} :: {} :: {} {}".format(unicode(self.section),
            self.section_order, self.name, '(inactive)' if not self.is_active else ''))

    # TODO: when the time is come, use unified model
    def object(self):
        return ENTITY_MODEL[self.object_type].objects.get(id=self.object_id)
