# -*- coding: utf-8 -*-
from organization.models import Organization
from komoo_resource.models import Resource
from komoo_project.models import Project
from need.models import Need
from community.models import Community
from investment.models import Investment
from proposal.models import Proposal
from main.models import ContactsField


def _migrate_model(model, custom_data=None):
    for obj in model.objects.all():
        obj.contacts = ContactsField.json_field_defaults
        obj.contacts['other'] = getattr(obj, 'contact', None) or None
        if custom_data:
            custom_data(obj)
        obj.save()


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


def run():
    migrate_organizations()
    migrate_resources()
    migrate_projects()
    migrate_needs()
    migrate_communities()
    migrate_investments()
    migrate_proposals()
