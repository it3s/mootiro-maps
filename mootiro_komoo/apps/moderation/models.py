# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default

from django.db import models
from django.contrib.contenttypes import generic
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _


class ModerationManager(models.Manager):
    def get_for_object(self, obj, user=None):
        content_type = ContentType.objects.get_for_model(obj)
        kwargs = {
            'content_type__pk': content_type.pk,
            'object_id': obj.pk
        }
        if user:
            kwargs['user'] = user
        return self.filter(**kwargs)


class Moderation(models.Model):
    """
    Abuse report model. Should dinamically reference any table/object.
    """

    DELETION_REQUEST = 1
    SPAM = 2
    INAPPROPRIATE = 3
    TERMS_OF_USE = 4
    COPYRIGHT = 5
    MISLEADING = 6
    UNSAFE = 7
    UNRELATED = 8
    ANOTHER = 9

    TYPE = (
        (DELETION_REQUEST, _('Deletion requested by creator')),
        (SPAM, _('Spam')),
        (INAPPROPRIATE, _('Inappropriate')),
        (TERMS_OF_USE, _('Terms Of Use Violation')),
        (COPYRIGHT, _('Copyright Violation')),
        (MISLEADING, _('Misleading Content')),
        (UNSAFE, _('Unsafe Content')),
        (UNRELATED, _('Unrelated Content')),
        (ANOTHER, _('Another Reason')),
    )

    user = models.ForeignKey(User, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    reason = models.IntegerField(choices=TYPE, verbose_name=_('reason'))
    comment = models.CharField(max_length=1024, null=True, blank=True,
            verbose_name=_('comment'))
    # dynamic ref
    content_type = models.ForeignKey(ContentType,  null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    objects = ModerationManager()

    class Meta:
        verbose_name = _('report')
        verbose_name_plural = _('reports')

    @property
    def object_name(self):
        return self.content_object.name

    @property
    def object_admin_url(self):
        return reverse('admin:%s_%s_change' % (self.content_type.app_label,
                                               self.content_type.model),
                args=(self.object_id,))

    @classmethod
    def get_reports_for(klass, obj):
        obj_content_type = ContentType.objects.get_for_model(obj)
        return Moderation.objects.filter(content_type=obj_content_type, object_id=obj.id)
