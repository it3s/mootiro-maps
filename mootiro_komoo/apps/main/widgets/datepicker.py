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
