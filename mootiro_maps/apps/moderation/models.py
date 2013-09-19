# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default

from django.db import models
from django.contrib.contenttypes import generic
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from authentication.models import User


class ModerationManager(models.Manager):
    def get_for_object_or_create(self, obj):
        content_type = ContentType.objects.get_for_model(obj)
        kwargs = {
            'content_type': content_type,
            'object_id': obj.pk
        }
        moderation, created = self.get_or_create(**kwargs)
        return moderation

    def get_for_object(self, obj):
        content_type = ContentType.objects.get_for_model(obj)
        kwargs = {
            'content_type': content_type,
            'object_id': obj.pk
        }
        moderation = self.filter(**kwargs)
        return moderation


class Moderation(models.Model):
    """Moderation model"""
    # dynamic ref
    content_type = models.ForeignKey(ContentType,  null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    objects = ModerationManager()

    def __unicode__(self):
        return '{} ({})'.format(self.content_object, self.content_type)


class Report(models.Model):
    """Abuse report model. Should dinamically reference any table/object."""
    (DELETION_REQUEST, SPAM, INAPPROPRIATE, TERMS_OF_USE, COPYRIGHT,
    WRONG, ANOTHER) = range(7)

    REASON_NAMES = {
        DELETION_REQUEST: _('Request for deletion'),
        SPAM: _('Spam'),
        INAPPROPRIATE: _('Inappropriate'),
        TERMS_OF_USE: _('Violation of Terms of Use'),
        COPYRIGHT: _('Copyright Violation'),
        WRONG: _('Wrong information'),
        ANOTHER: _('Other')
    }

    moderation = models.ForeignKey(Moderation, blank=False, null=False,
                                   related_name='reports')
    user = models.ForeignKey(User, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    reason = models.IntegerField(choices=REASON_NAMES.items(),
                                 verbose_name=_('reason'))
    comment = models.CharField(max_length=1024, null=True, blank=True,
                               verbose_name=_('comment'))

    class Meta:
        verbose_name = _('report')
        verbose_name_plural = _('reports')

    def __unicode__(self):
        return '{} (reported by {})'.format(self.reason_name, self.user)

    @property
    def object_name(self):
        return self.moderation.content_object.name

    @property
    def reason_name(self):
        return '{}'.format(self.REASON_NAMES[int(self.reason)])

    @property
    def object_admin_url(self):
        return reverse('admin:%s_%s_change' % (self.content_type.app_label,
                                               self.content_type.model),
                args=(self.object_id,))

    @classmethod
    def get_reports_for(klass, obj):
        obj_content_type = ContentType.objects.get_for_model(obj)
        moderation = Moderation.objects.filter(content_type=obj_content_type,
                                               object_id=obj.id)
        return klass.objects.filter(moderation=moderation)
