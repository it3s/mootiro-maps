# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default

from django import forms


class Datepicker(forms.DateInput):

    def render_js(self, field_id):
        js = u"""
        $("#%(field_id)s").datepicker();
        """ % {
            'field_id': field_id,
        }
        return js

    def render(self, name, value, **attrs):
        final_attrs = self.build_attrs(attrs, name=name)

        if not 'id' in self.attrs:
            final_attrs['id'] = 'id_%s' % name

        html = u"""
        %(textfield)s
        <script type="text/javascript"><!--//
          %(js)s
        //--></script>
        """ % {
            'textfield': super(Datepicker, self) \
                            .render(name, value, final_attrs),
            'js': self.render_js(final_attrs['id'])
        }
        return html


class ConditionalField(forms.CheckboxInput):

    def __init__(self, show_on_active='', hide_on_active='', *a, **kw):
        self.show_on_active = show_on_active
        self.hide_on_active = hide_on_active
        super(ConditionalField, self).__init__(*a, **kw)

    def render_js(self, checkbox_id):
        js = u"""
        $("#%(checkbox_id)s").on("click", function (event) {
            var st = Boolean($(this).attr('checked'));
            if (st) {
                $("%(show_on_active)s").show();
                $("%(hide_on_active)s").hide();
            } else {
                $("%(show_on_active)s").hide();
                $("%(hide_on_active)s").show();
            }
        });
        $(function () {
            $("#%(checkbox_id)s").triggerHandler("click");
        });
        """ % {
            'show_on_active': self.show_on_active,
            'hide_on_active': self.hide_on_active,
            'checkbox_id': checkbox_id,
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
            'checkbox': super(ConditionalField, self).render(name, value, final_attrs),
            'js': self.render_js(final_attrs['id'])
        }
        return html
