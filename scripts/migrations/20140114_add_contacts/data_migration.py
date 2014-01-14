# -*- coding: utf-8 -*-
from organization.models import Organization
from main.utils import ContactsField

def migrate_organizations():
    for org in Organization.objects.all():
      org.contacts = ContactsField.json_field_defaults
      org.contacts['site'] = org.link or None
      org.contacts['---'] = org.contact or None
      org.save()

def run():
  migrate_organizations()
