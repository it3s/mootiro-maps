# -*- coding: utf-8 -*-
from django.contrib.gis.db import models
from lib.taggit.managers import TaggableManager
from komoo_map.models import GeoRefModel
from authentication.models import User


class CommonDataMixin(models.Model):
    """ Common attributes and behavior"""
    name = models.CharField(max_length=512)
    description = models.TextField()

    creator = models.ForeignKey(User, editable=False, null=True,
                        related_name='created_%(class)s')
    creation_date = models.DateTimeField(auto_now_add=True)
    last_editor = models.ForeignKey(User, editable=False, null=True,
                        blank=True, related_name='last_edited_%(class)s')
    last_update = models.DateTimeField(auto_now=True)

    tags = TaggableManager()

    class Meta:
        abstract = True


class CommonObject(GeoRefModel, CommonDataMixin):
    """
    All mapped objects inherit from this object so then can be
    inter-changeable. This model holds the 'true PK'' for a mapped
    object and all references to them should be made through the
    CommonObject's id.
    """
    type = models.CharField(max_length=256)

    def to_dict(self):
        return {}

    def from_dict(self, data):
        return None

    def __init__(self, *args, **kwargs):
        super(CommonObject, self).__init__(*args, **kwargs)
        if hasattr(self, 'object_type') and self.object_type:
            self.type = self.object_type

    def __unicode__(self):
        return unicode('[{}] {}'.format(self.type, self.name))
