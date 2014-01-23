# -*- coding: utf-8 -*-
from organization.models import Organization
from komoo_resource.models import Resource
from komoo_project.models import Project
from main.models import ContactsField


def migrate_organizations():
    for org in Organization.objects.all():
        org.contacts = ContactsField.json_field_defaults
        org.contacts['site'] = org.link or None
        org.contacts['other'] = org.contact or None
        org.save()


def migrate_resources():
    for res in Resource.objects.all():
        res.contacts = ContactsField.json_field_defaults
        res.contacts['other'] = res.contact or None
        res.save()


def migrate_projects():
    for proj in Project.objects.all():
        proj.contacts = ContactsField.json_field_defaults
        proj.contacts['other'] = proj.contact or None
        proj.save()


def run():
    migrate_organizations()
    migrate_resources()
    migrate_projects()
