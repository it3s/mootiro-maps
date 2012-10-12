# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse

from komoo_user.models import KomooUser as User


class Comment(models.Model):
    """
    Comments models. Should dinamically reference any table/object.
    For querying purposes we need to add the above entry on those models that
    need to have Comments:
        comments = generic.GenericRelation(Comment)
    """
    author = models.ForeignKey(User, blank=True, null=True)
    comment = models.CharField(max_length=1024)
    parent = models.ForeignKey('Comment', null=True, blank=True,
                related_name="comment_parent")
    sub_comments = models.IntegerField(blank=True, default=0)
    pub_date = models.DateTimeField(auto_now_add=True)
    # dynamic ref
    content_type = models.ForeignKey(ContentType,  null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    def save(self, *args, **kwargs):
        if self.parent:
            parent = self.parent
            parent.sub_comments += 1
            parent.save()
        return super(Comment, self).save(*args, **kwargs)

    @classmethod
    def get_comments_for(klass, obj):
        obj_content_type = ContentType.objects.get_for_model(obj)
        return Comment.objects.filter(content_type=obj_content_type, object_id=obj.id)

    @classmethod
    def comments_count_for(klass, obj):
        obj_content_type = ContentType.objects.get_for_model(obj)
        return Comment.objects \
                    .filter(content_type=obj_content_type, object_id=obj.id) \
                    .count()

    @property
    def admin_url(self):
        return reverse('admin:{}_{}_change'.format(self._meta.app_label,
            self._meta.module_name), args=[self.id])
