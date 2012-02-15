#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from itertools import chain

from django import forms
from django.forms.widgets import flatatt
from django.utils.simplejson import JSONEncoder
from django.utils.html import escape, conditional_escape
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe

from annoying.functions import get_config


class JQueryAutoComplete(forms.TextInput):
    def __init__(self, source, value_field=None, options={}, attrs={}):
        """source can be a list containing the autocomplete values or a
        string containing the url used for the XHR request.

        For available options see the autocomplete sample page::
        http://jquery.bassistance.de/autocomplete/"""

        self.value_field = value_field
        self.options = options
        self.attrs = {'autocomplete': 'off'}
        self.source = source

        self.attrs.update(attrs)

    def render_js(self, label_id, value_id):
        if isinstance(self.source, list):
            source = JSONEncoder().encode(self.source)
        elif isinstance(self.source, basestring):
            source = "%s" % escape(self.source)
        else:
            print type(self.source)
            raise ValueError('source type is not valid')

        js = u"""
        $("#%(label_id)s").autocomplete({
            source: "%(source)s",
            focus: function(event, ui) {
                $("#%(label_id)s").val(ui.item.label);
                return false;
            },
            select: function(event, ui) {
                $("#%(label_id)s").val(ui.item.label);
                $("#%(value_id)s").val(ui.item.value);
                return false;
            }
        });
        """ % {
            'source': source,
            'label_id': label_id,
            'value_id': value_id
        }

        return js

    def render(self, name, value=None, attrs=None):
        final_attrs = self.build_attrs(attrs, name=name)
        if value:
            final_attrs['value'] = escape(unicode(value))

        if not 'id' in self.attrs:
            final_attrs['id'] = 'id_%s' % name

        return u'''<input type="text" %(attrs)s/>
        <script type="text/javascript"><!--//
        %(js)s//--></script>
        ''' % {
            'name': name,
            'attrs': flatatt(final_attrs),
            'js': self.render_js(final_attrs['id'], "id_%s" % self.value_field),
        }


class Tagsinput(forms.TextInput):
    """Widget for using JQuery Tags Input Plugin by xoxco.com
    See http://xoxco.com/projects/code/tagsinput/
    """

    class Media:
        css = {'all': ('lib/tagsinput/jquery.tagsinput.css',)}
        js = ('lib/tagsinput/jquery.tagsinput.min.js',)

        
    def __init__(self, autocomplete_url="", options={}, attrs={}):
        self.autocomplete_url = autocomplete_url
        self.options = options
        self.attrs = attrs

    def render_js(self, elem_id):
        if self.autocomplete_url:
            options_str = "{autocomplete_url: '%s'}" % self.autocomplete_url
        else:
            options_str = ""

        js = u"""
        $('#%(elem_id)s').tagsInput(%(options)s);
        """ % {
            'elem_id': elem_id,
            'options': options_str,
        }
        return js

    def render(self, name, value=None, attrs=None):
        final_attrs = self.build_attrs(attrs, name=name)

        if not 'id' in self.attrs:
            final_attrs['id'] = 'id_%s' % name

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


class ImageSwitch(forms.CheckboxInput):

    class Media:
        js = ('lib/jquery.imagetick.min.js',)

    def __init__(self, image_tick, image_no_tick, attrs=None):
        super(ImageSwitch, self).__init__(attrs)
        self.image_tick = get_config("STATIC_URL", "") + image_tick
        self.image_no_tick = get_config("STATIC_URL", "") + image_no_tick

    def render_js(self, checkbox_id):
        js = u"""
        $("#%(checkbox_id)s").imageTick({
            tick_image_path: "%(image_tick)s",
            no_tick_image_path: "%(image_no_tick)s"
        });
        """ % {
            'checkbox_id': checkbox_id,
            'image_tick': self.image_tick,
            'image_no_tick': self.image_no_tick,
        }
        return js

    def render(self, name, value, **attrs):
        final_attrs = self.build_attrs(attrs, name=name)

        if not 'id' in self.attrs:
            final_attrs['id'] = 'id_%s' % name

        html = u"""
        %(checkbox)s
        <script type="text/javascript"><!--//
          %(js)s
        //--></script>
        """ % {
            'checkbox': super(ImageSwitch, self).render(name, value, final_attrs),
            'js': self.render_js(final_attrs['id'])
        }
        return html


class ImageSwitchMultiple(forms.CheckboxSelectMultiple):

    class Media:
        js = ('lib/jquery.imagetick.min.js',)

    def render(self, name, value, attrs=None, choices=()):
        if value is None: value = []
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs, name=name)
        output = [u'<ul>']
        # Normalize to strings
        str_values = set([force_unicode(v) for v in value])
        for i, (option_value, option_label) in enumerate(chain(self.choices, choices)):
            # If an ID attribute was given, add a numeric index as a suffix,
            # so that the checkboxes don't all have the same ID attribute.
            if has_id:
                final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i))
                label_for = u' for="%s"' % final_attrs['id']
            else:
                label_for = ''

            cb = ImageSwitch("environment-off.png", "environment-on.png", attrs=final_attrs)
            option_value = force_unicode(option_value)
            rendered_cb = cb.render(name, option_value)
            option_label = conditional_escape(force_unicode(option_label))
            #output.append(u'<li>%s <label%s>%s</label></li>' % (rendered_cb, label_for, option_label))
            output.append(u'<li title="%s">%s</li>' % (option_label, rendered_cb))
        output.append(u'</ul>')
        return mark_safe(u'\n'.join(output))