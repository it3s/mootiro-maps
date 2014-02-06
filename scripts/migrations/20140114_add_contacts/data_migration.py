# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re
from organization.models import Organization
from komoo_resource.models import Resource
from komoo_project.models import Project
from need.models import Need
from community.models import Community
from investment.models import Investment
from proposal.models import Proposal
from authentication.models import User
from main.models import ContactsField


addr_regexp = ".*Endereço: (?P<address>.*)[\r]?\n"
postal_and_city_regexp = ".*CEP: (?P<postal_code>.*), (?P<city>.*)[\r]?\n"
phone_regexp = ".*Telefone: (?P<phone>.*)[\r]?\n"
email_regexp = ".*E[-]?mail: (?P<email>.*)[\r]?[\n]?"


def _parse(ct, pattern, keys, with_dict=False):
    matches = re.compile(pattern, re.IGNORECASE).search(ct['other'])
    if matches:
        for key in keys:
            ct[key] = matches.groupdict().get(key, None)
        ct['other'] = ct['other'].replace(matches.group(), "")
    return ct


def _clean_trailing_whitespaces_and_newlines(ct):
    ct['other'] = ct['other'].rstrip()
    if ct['other'] == '':
        ct['other'] = None
    return ct


def _extract_contact_info(ct):
    ct = _parse(ct, addr_regexp, ['address'])
    ct = _parse(ct, postal_and_city_regexp, ['postal_code', 'city'], with_dict=True)
    ct = _parse(ct, phone_regexp, ['phone'])
    ct = _parse(ct, email_regexp, ['email'])

    ct = _clean_trailing_whitespaces_and_newlines(ct)
    return ct


def _migrate_object(obj, custom_data=None):
    obj.contacts = ContactsField.defaults()
    obj.contacts['other'] = getattr(obj, 'contact', None) or None
    if custom_data:
        custom_data(obj)
    if obj.contacts['other']:
        obj.contacts['other'] = obj.contacts['other'].replace("**", "")
        obj.contacts = _extract_contact_info(obj.contacts)
    obj.save()


def _migrate_model(model, custom_data=None):
    for obj in model.objects.all():
        _migrate_object(obj, custom_data)


def migrate_organizations():
    def _custom_data(org):
        org.contacts['site'] = org.link or None
    _migrate_model(Organization, _custom_data)


def migrate_resources():
    _migrate_model(Resource)


def migrate_projects():
    _migrate_model(Project)


def migrate_needs():
    _migrate_model(Need)


def migrate_communities():
    _migrate_model(Community)


def migrate_investments():
    _migrate_model(Investment)


def migrate_proposals():
    _migrate_model(Proposal)


def migrate_users():

    _migrate_model(User)


def run():
    migrate_organizations()
    migrate_resources()
    migrate_projects()
    migrate_needs()
    migrate_communities()
    migrate_investments()
    migrate_proposals()
    migrate_users()
