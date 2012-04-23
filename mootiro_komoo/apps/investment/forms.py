# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default

from django import forms
from django.utils.translation import ugettext_lazy as _

from annoying.decorators import autostrip
from markitup.widgets import MarkItUpWidget
from crispy_forms.layout import *

from main.utils import MooHelper
from investment.models import Investment, Investor
from organization.models import Organization

from main.widgets import TaggitWidget, Datepicker, ConditionalField, \
    Autocomplete


@autostrip
class InvestmentForm(forms.ModelForm):

    class Meta:
        model = Investment
        fields = ('title', 'description', 'investor_type', 'anonymous_investor',
            'investor_organization', 'investor_person', 'over_period', 'date',
            'end_date', 'currency', 'value', 'tags')

    title = forms.CharField()
    description = forms.CharField(widget=MarkItUpWidget())

    investor_type = forms.ChoiceField(
        choices=Investor.TYPE_CHOICES,
        initial='ORG',
        widget=forms.RadioSelect,
        required=True
    )

    anonymous_investor = forms.BooleanField(
        widget=ConditionalField(hide_on_active="#investment_form .investor_fields"),
        required=False
    )

    # FIXME: the urls below should not be hardcoded. They should be calculated
    # with reverse_lazy function, which is not implemented in Django 1.3 yet.

    investor_organization = forms.ModelChoiceField(
        queryset=Organization.objects.all(),
        widget=Autocomplete(Organization, "/organization/search_by_name"),
        required=False,
        label="Investor"
    )
    investor_person = forms.CharField(label="Investor", required=False)

    # this field is needed to avoid creating duplicated instances
    investor = forms.ModelChoiceField(
        queryset=Investor.objects.all(),
        required=False
    )

    date = forms.DateField(widget=Datepicker())
    end_date = forms.DateField(widget=Datepicker(), required=False)
    over_period = forms.BooleanField(
        widget=ConditionalField(show_on_active="#div_id_end_date"),
        required=False
    )

    tags = forms.Field(
        widget=TaggitWidget(autocomplete_url="/investment/tag_search"),
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
            Div(
                "investor_organization",
                "investor_person",
                css_class="investor_fields"
            ),
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

    def clean(self):
        cleaned_data = super(InvestmentForm, self).clean()

        # investor validation
        current_investor = cleaned_data.pop("investor")
        anonymous_investor = cleaned_data.pop("anonymous_investor")
        investor_type = cleaned_data.pop("investor_type")
        investor_organization = cleaned_data.pop("investor_organization")
        investor_person = cleaned_data.pop("investor_person")
        if not anonymous_investor:
            msg = _("Invalid investor.")
            if investor_type == "ORG" and not investor_organization:
                self._errors["investor_organization"] = self.error_class([msg])
            elif investor_type == "PER" and not investor_person:
                self._errors["investor_person"] = self.error_class([msg])
        # investor coercing
        if anonymous_investor:
            investor = ""
        elif investor_type == 'ORG':
            investor = investor_organization
        elif investor_type == 'PER':
            investor = investor_person

        investor, created = Investor.get_or_create_for(investor,
                                current=current_investor)
        if created:
            investor.save()

        cleaned_data['investor'] = investor

        return cleaned_data
