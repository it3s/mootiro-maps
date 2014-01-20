# -*- coding: utf-8 -*-

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

    def key_name(self, key):
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
            '---': '---',
        }[key]


