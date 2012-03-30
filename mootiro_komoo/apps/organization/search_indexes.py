# -*- coding: utf-8 -*-
from datetime import datetime
from haystack import indexes
from haystack import site
from organization.models import Organization, OrganizationBranch


class OrganizationIndex(indexes.RealTimeSearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    name = indexes.EdgeNgramField(model_attr='name', boost=2.0)
    slug = indexes.EdgeNgramField(model_attr='slug', boost=2.0)
    # creator = indexes.CharField(model_attr='creator', null=True)
    creation_date = indexes.DateTimeField(model_attr='creation_date')

    def index_queryset(self):
        """Used when the entire index for model is updated."""
        return Organization.objects.filter(creation_date__lte=datetime.now())

site.register(Organization, OrganizationIndex)


class OrganizationBranchIndex(indexes.RealTimeSearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    name = indexes.EdgeNgramField(model_attr='name', boost=2.0)
    slug = indexes.EdgeNgramField(model_attr='slug', boost=2.0)

    creation_date = indexes.DateTimeField(model_attr='creation_date')

    def index_queryset(self):
        return OrganizationBranch.objects.filter(creation_date__lte=datetime.now())

site.register(OrganizationBranch, OrganizationBranchIndex)
