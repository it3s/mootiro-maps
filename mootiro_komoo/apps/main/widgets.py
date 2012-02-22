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
from django.template.defaultfilters import slugify

from annoying.functions import get_config


class JQueryAutoComplete(forms.TextInput):
    """Widget that uses a JQuery autocomplete façade to fill a hidden field.
    Usually to be used on ForeignKey fields.
        label_id: html id of the visible autocomplete field;
        value_id: html id of the hidden field that contains data to be persisted;
    """
    def __init__(self, source_url, *a, **kw):
        self.source_url = source_url
        super(JQueryAutoComplete, self).__init__(*a, **kw)

    def render_js(self, label_id, value_id):
        js = u"""
        $("#%(label_id)s").autocomplete({
            source: "%(source_url)s",
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
            'source_url': self.source_url,
            'label_id': label_id,
            'value_id': value_id
        }
        return js

    def render(self, name, value=None, attrs=None):
        value_id = 'id_%s' % name  # id_fieldname
        label_id = '%s_autocomplete' % value_id  # id_fieldname_autocomplete

        value_attrs = dict(id=value_id, name=name, value=value)

        # attrs is consumed by the label field (autocomplete)
        label_attrs = self.build_attrs(attrs, name=name)
        if value:
            # TODO: get label for initial bounded value. How?
            label_attrs['value'] = escape(unicode(value))
        if not 'id' in self.attrs:
            label_attrs['id'] = label_id

        html = u'''
        <input type="hidden" %(value_attrs)s />
        <input type="text" %(label_attrs)s />
        <script type="text/javascript"><!--//
          %(js)s
        //--></script>
        ''' % {
            'rendered_value_field': super(JQueryAutoComplete, self).render(name, value),
            'value_attrs': flatatt(value_attrs),
            'label_attrs': flatatt(label_attrs),
            'js': self.render_js(label_id, value_id),
        }
        return html


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

    def __init__(self, image_tick, image_no_tick, attrs=None, *a, **kw):
        super(ImageSwitch, self).__init__(attrs, *a, **kw)
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
        if value is None:
            value = []
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

            image_tick = "%s-tick.png" % slugify(option_label)
            image_no_tick = "%s-no-tick.png" % slugify(option_label)
            cb = ImageSwitch(image_tick, image_no_tick, attrs=final_attrs,
                    check_test=lambda value: value in str_values)
            option_value = force_unicode(option_value)
            rendered_cb = cb.render(name, option_value)
            option_label = conditional_escape(force_unicode(option_label))
            output.append(u'<li title="%s">%s</li>' % (option_label, rendered_cb))
        output.append(u'</ul>')
        return mark_safe(u'\n'.join(output))
