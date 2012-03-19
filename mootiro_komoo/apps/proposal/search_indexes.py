# -*- coding: utf-8 -*-
from datetime import datetime
from haystack import indexes
from haystack import site
from proposal.models import Proposal


class ProposalIndex(indexes.SearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.EdgeNgramField(model_attr='title', boost=2.0)
    description = indexes.CharField(model_attr='description')
    creator = indexes.CharField(model_attr='creator')
    creation_date = indexes.DateTimeField(model_attr='creation_date')

    def index_queryset(self):
        """Used when the entire index for model is updated."""
        return Proposal.objects.filter(creation_date__lte=datetime.now())

site.register(Proposal, ProposalIndex)
