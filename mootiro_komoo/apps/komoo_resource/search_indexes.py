# -*- coding: utf-8 -*-
from datetime import datetime
from haystack import indexes
from haystack import site
from komoo_resource.models import Resource


class ResourceIndex(indexes.SearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    creator = indexes.CharField(model_attr='creator')
    creation_date = indexes.DateTimeField(model_attr='creation_date')
    description = indexes.CharField(model_attr='description')

    def index_queryset(self):
        """Used when the entire index for model is updated."""
        return Resource.objects.filter(creation_date__lte=datetime.now())

site.register(Resource, ResourceIndex)
