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


addr_regexp = re.compile(
    ".*Endereço:.*\n", re.IGNORECASE)

postal_and_city_regexp = re.compile(
    ".*CEP: (?P<postal_code>.*), (?P<city>.*)\n", re.IGNORECASE)


def _extract_contact_info(ct):

    # extract address
    matches = addr_regexp.search(ct['other'])
    if matches:
        ct['address'] = matches.group()\
                               .replace("**Endereço:**", "")\
                               .replace("Endereço:", "")\
                               .replace("\n", "")\
                               .replace("\t", "")\
                               .strip()
        ct['other'] = ct['other'].replace(matches.group(), "")

    # extract postal code and city
    matches = postal_and_city_regexp.search(ct['other'])
    if matches:
        ct['postal_code'] = matches.groupdict().get('postal_code', None)
        ct['city'] = matches.groupdict().get('city', None)
        ct['other'] = ct['other'].replace(matches.group(), "")

    return ct


def _migrate_object(obj, custom_data=None):
    obj.contacts = ContactsField.json_field_defaults
    obj.contacts['other'] = getattr(obj, 'contact', None) or None
    if custom_data:
        custom_data(obj)
    if obj.contacts['other']:
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
