# -*- coding: utf-8 -*-
from django.utils.translation import ugettext as _
from jsonfield import JSONField


class ContactsField(JSONField):
    """
    Splited Contacts model Field.
    Uses a JSON Field with predefined keys.
    """

    json_field_defaults = {
        'address': None,
        'compl': None,
        'city': None,
        'postal_code': None,
        'phone': None,
        'facebook': None,
        'email': None,
        'twitter': None,
        'site': None,
        '---': None,
    }

    def __init__(self, *args, **kwargs):
        # guarantes we have all keys by default
        kwargs.update(default=self.json_field_defaults)
        super(ContactsField, self).__init__(*args, **kwargs)

    @classmethod
    def key_names(self):
        """ Translated key name """
        return {
            'address': _('Address'),
            'compl': _('Complement'),
            'city': _('City'),
            'postal_code': _('Postal Code'),
            'phone': _('Phone'),
            'facebook': _('Facebook'),
            'email': _('E-mail'),
            'twitter': _('Twitter'),
            'site': _('Web Site'),
            '---': _('Others'),
        }

    @classmethod
    def key_name(self, key):
        """ Translated key name"""
        return self.key_names()[key]


