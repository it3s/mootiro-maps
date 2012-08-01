#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default

from django.utils.translation import ugettext_lazy as _
from django import forms
from django.forms.widgets import flatatt
from django.utils.html import escape


class MultipleAutocompleteBase(forms.TextInput):
    """User friendly text input for many to many relationship fields.

    The JQuery Tags Input Plugin by xoxco.com (seehttp://xoxco.com/projects/code/tagsinput/)
    provides the friendly tag insertion interface.

    This class can be easily extended to work with different Field types by
    overwriting 'widget_to_field' and 'field_to_widget' converter methods.
    """

    class Media:
        css = {'all': ('lib/tagsinput/jquery.tagsinput.css',)}
        js = ('lib/tagsinput/jquery.tagsinput.min.js',)

    def __init__(self, autocomplete_url="", options={}, attrs={}):
        """Constructs the widget.

        - autocomplete_url: url that accepts a 'term' GET variable and returns a
          json list containing names that matches the given term.
        """
        self.autocomplete_url = autocomplete_url
        self.options = options
        self.attrs = attrs

    def widget_to_field(self, x):
        return x

    def field_to_widget(self, x):
        return x

    def value_from_datadict(self, data, files, name):
        s = data.get(name, '')  # comma separated string
        l = [self.widget_to_field(v) for v in s.split(',')] if s else []
        return l

    def render_js(self, elem_id):
        options_str = """
        {
          'autocomplete_url':'%(url)s',
          'defaultText':'%(text)s',
          'height':'auto',
          'width':'100%%'
        }
        """ % {
            'url': self.autocomplete_url,
            'text': _("add a tag")
        }

        js = u"""
        $(function(){
            $('#%(elem_id)s').tagsInput(%(options)s);
        });
        """ % {
            'elem_id': elem_id,
            'options': options_str,
        }
        return js

    def render(self, name, value=None, attrs=None):
        final_attrs = self.build_attrs(attrs, name=name)

        if not 'id' in self.attrs:
            final_attrs['id'] = 'id_%s' % name
        if value:
            strings = [v if type(v) == unicode else self.field_to_widget(v) \
                        for v in value]
            final_attrs['value'] = ", ".join(strings)

        html = u"""
        <input %(attrs)s"/>
        <script type="text/javascript"><!--//
          %(js)s
        //--></script>
        """ % {
            'name': name,
            'attrs': flatatt(final_attrs),
            'js': self.render_js(final_attrs['id'])
        }
        return html


class Tagsinput(MultipleAutocompleteBase):
    """Widget for inputting 'tag-like' objects.

    Uses 'name' as the default attribute for showing.
    """

    def __init__(self, model, *a, **kw):
        self.model = model
        super(Tagsinput, self).__init__(*a, **kw)

    def widget_to_field(self, tag_name):
        instance, created = self.model.objects.get_or_create(name=tag_name)
        return instance.id

    def field_to_widget(self, tag_id):
        instance = self.model.objects.get(id=tag_id)
        return unicode(instance.name)


class TaggitWidget(MultipleAutocompleteBase):
    """Follows django-taggit api"""

    def widget_to_field(self, tag_name):
        return tag_name

    def field_to_widget(self, instance):
        return unicode(instance.tag)
