# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default

from django import forms
from django.forms import ModelForm, CharField

from annoying.decorators import autostrip
from markitup.widgets import MarkItUpWidget

from main.utils import MooHelper
from investment.models import Investment
from community.models import Community

from main.widgets import Autocomplete, TaggitWidget
# from need.models import Need, NeedCategory, TargetAudience


@autostrip
class InvestmentForm(ModelForm):

    class Meta:
        model = Investment

    description = CharField(widget=MarkItUpWidget())
    tags = forms.Field(
        widget=TaggitWidget(autocomplete_url="/need/tag_search"),
        required=False
    )

    def __init__(self, *a, **kw):
        # Crispy forms configuration
        self.helper = MooHelper()
        self.helper.form_id = "investment_form"

        super(InvestmentForm, self).__init__(*a, **kw)
