#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from itertools import chain

from django import forms
from django.utils.html import conditional_escape
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from annoying.functions import get_config


class ImageSwitch(forms.CheckboxInput):

    class Media:
        js = ('lib/jquery.imagetick.js',)

    def __init__(self, image_tick, image_no_tick, attrs=None, prefix='', *a, **kw):
        super(ImageSwitch, self).__init__(attrs, *a, **kw)
        self.image_tick = get_config("STATIC_URL", "") + image_tick
        self.image_no_tick = get_config("STATIC_URL", "") + image_no_tick
        self.prefix = prefix + '_' if prefix else ''

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
            final_attrs['id'] = '%sid_%s' % (self.prefix, name)

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
        js = ('lib/jquery.imagetick.js',)

    def __init__(self, get_image_tick, get_image_no_tick, show_names=False,
            prefix='', i18n=True, *a, **kw):
        super(ImageSwitchMultiple, self).__init__(*a, **kw)
        self.get_image_tick = get_image_tick
        self.get_image_no_tick = get_image_no_tick
        self.show_names = show_names
        self.i18n = i18n
        self.prefix = prefix + '_' if prefix else ''

    def render(self, name, value, attrs=None, choices=()):
        if value is None:
            value = []
        name = '%s%s' % (self.prefix, name)
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs, name=name)
        output = [u'<ul><span id="%s"></span>' % final_attrs['id']]
        # Normalize to strings
        str_values = set([force_unicode(v) for v in value])
        for i, (option_value, option_label) in enumerate(chain(self.choices, choices)):
            # If an ID attribute was given, add a numeric index as a suffix,
            # so that the checkboxes don't all have the same ID attribute.
            if has_id:
                final_attrs = dict(final_attrs, id='%s%s_%s' % (self.prefix, attrs['id'], i))

            image_tick = self.get_image_tick(option_label)
            image_no_tick = self.get_image_no_tick(option_label)
            cb = ImageSwitch(image_tick, image_no_tick, attrs=final_attrs,
                    check_test=lambda value: value in str_values)
            option_value = force_unicode(option_value)
            rendered_cb = cb.render(name, option_value)
            option_label = conditional_escape(force_unicode(option_label))
            if self.show_names:
                label = _(option_label) if self.i18n else option_label
                list_item = u'<li><div title="{0}" class="img-holder" data-original-label="{2}">{1}</div><span>{0}</span></li>' \
                    .format(label, rendered_cb, option_label)
            else:
                list_item = u'<li title="%s">%s</li>' % (option_label, rendered_cb)
            output.append(list_item)
        output.append(u'</ul>')
        return mark_safe(u'\n'.join(output))
