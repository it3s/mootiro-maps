# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django.db import models
from django.contrib.auth.models import User


class Comment(models.Model):
    author = models.ForeignKey(User, blank=True, null=True)
    comment = models.CharField(max_length=1024)
    parent = models.ForeignKey('Comment', null=True, blank=True, related_name="comment_parent")
    sub_comments = models.IntegerField(blank=True, default=0)
    pub_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.parent:
            parent = self.parent
            parent.sub_comments += 1
            parent.save()
        return super(Comment, self).save(*args, **kwargs)
