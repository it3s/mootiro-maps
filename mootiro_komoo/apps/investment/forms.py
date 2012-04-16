# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default

from django import forms
from django.forms import ModelForm

from annoying.decorators import autostrip
from markitup.widgets import MarkItUpWidget
from crispy_forms.layout import *

from main.utils import MooHelper
from investment.models import Investment, Investor
from organization.models import Organization

from main.widgets import TaggitWidget, Datepicker, ConditionalField, \
    Autocomplete


@autostrip
class InvestmentForm(ModelForm):

    class Meta:
        model = Investment
        initial = {'intestor_type': 'ORG'}

    description = forms.CharField(widget=MarkItUpWidget())

    investor_type = forms.ChoiceField(
        choices=Investor.TYPE_CHOICES,
        initial='ORG',
        widget=forms.RadioSelect,
        required=True
    )
    anonymous_investor = forms.BooleanField(
        # widget=ConditionalField(hide_on_active="#div_"),
        required=False
    )

    # FIXME: the urls below should not be hardcoded. They should be calculated
    # with reverse_lazy function, which is not implemented in Django 1.3 yet.
    investor = forms.ModelChoiceField(
        queryset=Organization.objects.all(),
        widget=Autocomplete(Organization, "/organization/search_by_name"),
        required=False
    )

    date = forms.DateField(widget=Datepicker())
    end_date = forms.DateField(widget=Datepicker(), required=False)
    over_period = forms.BooleanField(
        widget=ConditionalField(show_on_active="#div_id_end_date"),
        required=False
    )

    tags = forms.Field(
        widget=TaggitWidget(autocomplete_url="/need/tag_search"),
        required=False
    )

    # TODO: value just validates if currency is set

    def __init__(self, *a, **kw):
        # Crispy forms configuration
        self.helper = MooHelper()
        self.helper.form_id = "investment_form"
        self.helper.layout = Layout(
            "title",
            "description",
            "investor_type",
            "anonymous_investor",
            "investor",
            "over_period",
            Row(
                "date",
                "end_date",
            ),
            Row(
                "currency",
                "value",
            ),
            "tags",
        )

        super(InvestmentForm, self).__init__(*a, **kw)
