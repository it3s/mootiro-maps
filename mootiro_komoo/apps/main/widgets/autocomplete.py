# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default

from django import forms
from django.forms.widgets import flatatt
from django.utils.translation import ugettext_lazy as _


class Autocomplete(forms.TextInput):
    """Widget that uses a JQuery autocomplete facade to fill a hidden field.
    Usually to be used on ForeignKey fields.
        label_id: html id of the visible autocomplete field
        value_id: html id of the hidden field that contains data to be persisted
    """
    def __init__(self, model, source_url, label_field="name", *a, **kw):
        self.model = model
        self.source_url = source_url
        super(Autocomplete, self).__init__(*a, **kw)

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
            },
            change: function(event, ui) {
                if(!ui.item || !$("#%(label_id)s").val()){
                    $("#%(value_id)s").val('');
                    $("#%(label_id)s").val('');
                }
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

        if not value:
            value = ""

        value_attrs = dict(id=value_id, name=name, value=value)

        # attrs is consumed by the label field (autocomplete)
        label_attrs = self.build_attrs(attrs)  # must not have 'name' attribute
        if value and value != 'None':
            label_attrs['value'] = self.model.objects.get(id=value)
        else:
            label_attrs['value'] = ''
        if not 'id' in self.attrs:
            label_attrs['id'] = label_id

        html = u'''
        <input type="hidden" %(value_attrs)s />
        <input type="text" %(label_attrs)s />
        <script type="text/javascript"><!--//
          %(js)s
        //--></script>
        ''' % {
            'value_attrs': flatatt(value_attrs),
            'label_attrs': flatatt(label_attrs),
            'js': self.render_js(label_id, value_id),
        }
        return html

    def clean(self, value, *a, **kw):
        try:
            if not value or value == 'None':
                return self.model()
            else:
                return self.model.objects.get(id=value)
        except:
            raise forms.ValidationError(_('invalid data'))


class AutocompleteWithFavorites(forms.TextInput):
    """
    Autocomplete field with favorites sugestion.
    Usually to be used on ForeignKey fields.
    If you provide a ad_url argument it can add a new entry.
        label_id: html id of the visible autocomplete field
        value_id: html id of the hidden field that contains data to be persisted
    """
    class Media:
        js = ('/static/lib/shortcut.js',)

    def __init__(self, model, source_url, favorites_query, help_text=None,
                 can_add=False, *args, **kwargs):
        self.model = model
        self.source_url = source_url
        self.query = favorites_query
        if not help_text:
            help_text = _('You can type above or select here')
        self.help_text = help_text
        self.can_add = can_add
        super(AutocompleteWithFavorites, self).__init__(*args, **kwargs)

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

                var select_item = $("#%(value_id)s_select option[value=" + ui.item.value + "]");
                if( select_item.length){
                    select_item.attr('selected', 'selected');
                }
                else {
                    $("#%(value_id)s_select option:selected").removeAttr('selected');
                }

                return false;
            }
        });
        """ % {'source_url': self.source_url, 'label_id': label_id,
               'value_id': value_id}

        if not self.can_add:
            #  if we can not add new values, the autocomplete should be
            #  cleaned when not selected
            js += u"""
            $("#%(label_id)s").bind(
            'autocompletechange', function(event, ui) {
                if(!ui.item || !$("#%(label_id)s").val()){
                    $("#%(value_id)s").val('');
                    $("#%(label_id)s").val('');
                }
            });
        """ % {'label_id': label_id, 'value_id': value_id}

        # select field behavior
        js += u"""
        $("#%(value_id)s_select").change(function(evt){
            var opt = $(this).find('option:selected');
            $('#%(label_id)s').val(opt.text());
            $('#%(value_id)s').val(opt.val());
        });
        """ % {'label_id': label_id, 'value_id': value_id}

        return js

    def render_select(self, value_id=None):
        count = self.query.count()
        select = u'''
        <select id="%(value_id)s_select" size="%(count)s">
        ''' % dict(count=count, value_id=value_id)
        for obj in self.query:
            select += u'<option value="%(id)s">%(label)s</option>' % {
                'label': obj, 'id': obj.id}
        select += u'''
        </select>
        <span style="color: #aaaaaa;">%(help_text)s</span>
        ''' % dict(help_text=self.help_text)
        return select

    def render(self, name, value=None, attrs=None):
        value_id = 'id_%s' % name  # id_fieldname
        label_id = '%s_autocomplete' % value_id  # id_fieldname_autocomplete

        value_attrs = dict(id=value_id, name=name, value=value or '')

        # attrs is consumed by the label field (autocomplete)
        if value:
            label_value = str(self.model.objects.get(pk=value))
        else:
            label_value = ''
        label_attrs = dict(id=label_id, name='%s_autocomplete' % name, value=label_value)

        html = u'''
        <input type="hidden" %(value_attrs)s />
        <input type="text" %(label_attrs)s />

        %(select)s
        ''' % {'value_attrs': flatatt(value_attrs),
               'label_attrs': flatatt(label_attrs),
               'select': self.render_select(value_id)}

        html += u'''
        <script type="text/javascript"><!--//
            $(document).ready(function(){
                %(js)s
            });
        //--></script>
        ''' % {'js': self.render_js(label_id, value_id)}
        return html
