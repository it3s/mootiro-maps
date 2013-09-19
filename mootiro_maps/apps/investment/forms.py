# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default

from django import forms
from django.utils.translation import ugettext_lazy as _

from annoying.decorators import autostrip
from markitup.widgets import MarkItUpWidget
from crispy_forms.layout import *
from ajaxforms import AjaxModelForm

from main.utils import MooHelper
from investment.models import Investment, Investor
from organization.models import Organization

from main.widgets import TaggitWidget, Datepicker, ConditionalField, \
    Autocomplete
from signatures.signals import notify_on_update


@autostrip
class InvestmentForm(AjaxModelForm):

    class Meta:
        model = Investment
        fields = ('title', 'short_description', 'description', 'investor_type',
                  'anonymous_investor', 'investor_organization',
                  'investor_person', 'over_period', 'date', 'end_date',
                  'currency', 'value', 'tags')

    _field_labels = {
        'title': _('Title'),
        'short_description': _('Short description'),
        'description': _('Description'),
        'investor_type': _('Investor type'),
        'anonymous_investor': _('Anonymous investor'),
        'investor_organization': _('Investor organization'),
        'investor_person': _('Investor person'),
        'over_period': _('Investment period'),
        'date': _('Date'),
        'end_date': _('End date'),
        'currency': _('Currency'),
        'value': _('Value'),
        'tags': _('Tags'),
    }

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
        self.helper = MooHelper(form_id="investment_form")
        self.helper.layout = Layout(
            "id",
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

        return super(InvestmentForm, self).__init__(*a, **kw)

    def clean_end_date(self):
        data = self.cleaned_data['end_date']
        if not self.cleaned_data['over_period']:
            data = None
        return data

    def clean(self):
        cleaned_data = super(InvestmentForm, self).clean()

        # investor validation
        current_investor = self.cleaned_data.pop("investor")
        anonymous_investor = self.cleaned_data.pop("anonymous_investor")
        investor_type = self.cleaned_data.pop("investor_type")
        investor_organization = self.cleaned_data.pop("investor_organization")
        investor_person = self.cleaned_data.pop("investor_person")
        if not anonymous_investor:
            self.validation('investor_organization', _("Invalid investor."),
                investor_type == "ORG" and not investor_organization)
            self.validation('investor_person', _("Invalid investor."),
                investor_type == "PER" and not investor_person)
        # investor coercing
        if anonymous_investor:
            investor = ""
        elif investor_type == 'ORG':
            investor = investor_organization
        elif investor_type == 'PER':
            investor = investor_person

        if investor != None:
            investor, created = Investor.get_or_create_for(investor,
                                    current=current_investor)
            self.cleaned_data['investor'] = investor
        else:
            created = False

        if created:
            investor.save()


        return cleaned_data

    @notify_on_update
    def save(self, *args, **kwargs):
        investment = super(InvestmentForm, self).save(commit=False)
        investor = self.cleaned_data['investor']
        investor.save()
        investment.investor = investor

        # why need to explicit save tags here?
        tags = self.cleaned_data['tags']
        investment.tags.set(*tags)

        investment.save()
        return investment
