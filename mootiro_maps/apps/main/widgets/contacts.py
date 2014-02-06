# # -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
import simplejson as json
from main.models import ContactsField


class ContactsWidget(forms.Widget):
    """Splited Contacts widget"""
    class Media:
        js = ('js/widgets/contacts.js', )

    def render(self, name, value={}, attrs=None):
        if not value:
            value = ContactsField.defaults()
        return """
            <div class="contacts-list">
            </div>
            <div>
                <input type="hidden" id="id_contacts" name="%(name)s" value='%(value)s' data-key-names='%(key_names)s'>
            </div>
        """  % {
            "name": name,
            "value": mark_safe(json.dumps(value)),
            "key_names": mark_safe(json.dumps(ContactsField.key_names())),
        }
