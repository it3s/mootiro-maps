# -*- coding: utf-8 -*-
from django.db import models
from authentication.models import User


class Tracking(models.Model):
    url = models.URLField(db_index=True)

    ip_address = models.IPAddressField(blank=True, null=True, default=None)
    visitor = models.ForeignKey(User, editable=False, null=True,
            related_name='visited')
    visited_date = models.DateTimeField(db_index=True, auto_now_add=True)

    @classmethod
    def count_unique_visits_for(cls, url):
        return cls.objects.filter(url=url).values('visitor').annotate(
                    dcount=models.Count('visitor')).count()

    @classmethod
    def count_visits_for(cls, url):
        return cls.objects.filter(url=url).count()

    @classmethod
    def get_visits_from(cls, user):
        return cls.objects.filter(visitor=user)

    @classmethod
    def get_visits_for(cls, url):
        return cls.objects.filter(url=url)

    @classmethod
    def get_anonymous_visits(cls):
        return cls.objects.filter(visitor=None)
