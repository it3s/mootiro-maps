#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from itertools import chain

from django import forms
from django.forms.widgets import flatatt
from django.utils.html import escape, conditional_escape
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe

from annoying.functions import get_config


class Autocomplete(forms.TextInput):
    """Widget that uses a JQuery autocomplete facade to fill a hidden field.
    Usually to be used on ForeignKey fields.
        label_id: html id of the visible autocomplete field
        value_id: html id of the hidden field that contains data to be persisted
    """
    def __init__(self, model, source_url, *a, **kw):
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

        value_attrs = dict(id=value_id, name=name, value=value)

        # attrs is consumed by the label field (autocomplete)
        label_attrs = self.build_attrs(attrs)  # must not have 'name' attribute
        if value:
            label_attrs['value'] = self.model.objects.get(id=value)
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
        if self.autocomplete_url:
            options_str = """
            { 'autocomplete_url': '%(url)s',
              'height':'auto',
              'width':'100%%', }
            """ % {
                'url': self.autocomplete_url,
            }

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
        if value:
            strings = [v if type(v) == unicode else self.field_to_widget(v) \
                        for v in value]
            final_attrs['value'] = ", ".join([escape(s) for s in strings])

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

    def __init__(self, get_image_tick, get_image_no_tick, show_names=False, *a, **kw):
        super(ImageSwitchMultiple, self).__init__(*a, **kw)
        self.get_image_tick = get_image_tick
        self.get_image_no_tick = get_image_no_tick
        self.show_names = show_names

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

            image_tick = self.get_image_tick(option_label)
            image_no_tick = self.get_image_no_tick(option_label)
            cb = ImageSwitch(image_tick, image_no_tick, attrs=final_attrs,
                    check_test=lambda value: value in str_values)
            option_value = force_unicode(option_value)
            rendered_cb = cb.render(name, option_value)
            option_label = conditional_escape(force_unicode(option_label))
            if self.show_names:
                list_item = u'<li><div title="{0}" class="img-holder">{1}</div><span>{0}</span></li>' \
                    .format(option_label, rendered_cb)
            else:
                list_item = u'<li title="%s">%s</li>' % (option_label, rendered_cb)
            output.append(list_item)
        output.append(u'</ul>')
        return mark_safe(u'\n'.join(output))


class AutocompleteWithFavorites(forms.TextInput):
    """
    Autocomplete field with favorites sugestion.
    Usually to be used on ForeignKey fields.
        label_id: html id of the visible autocomplete field
        value_id: html id of the hidden field that contains data to be persisted
    """
    def __init__(self, model, source_url, favorites_query, *a, **kw):
        self.model = model
        self.source_url = source_url
        self.query = favorites_query
        super(AutocompleteWithFavorites, self).__init__(*a, **kw)

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
            },
            change: function(event, ui) {
                if(!ui.item || !$("#%(label_id)s").val()){
                    $("#%(value_id)s").val('');
                    $("#%(label_id)s").val('');
                }
            }
         });

        $("#%(value_id)s_select").change(function(evt){
            var opt = $(this).find('option:selected');
            $('#%(label_id)s').val(opt.text());
            $('#%(value_id)s').val(opt.val());
        });

        """ % {
            'source_url': self.source_url,
            'label_id': label_id,
            'value_id': value_id
        }
        return js

    def render_select(self, value_id=None):
        count = self.query.count()
        select = u'''
        <select id="%(value_id)s_select" size="%(count)s">
        ''' % dict(count=count, value_id=value_id)
        for obj in self.query:
            select += u'<option value="%(id)s">%(label)s</option>' % {
                'label': obj, 'id': obj.id}
        select == u'''
        </select>
        '''
        return select

    def render(self, name, value=None, attrs=None):
        value_id = 'id_%s' % name  # id_fieldname
        label_id = '%s_autocomplete' % value_id  # id_fieldname_autocomplete

        value_attrs = dict(id=value_id, name=name, value=value)

        # attrs is consumed by the label field (autocomplete)
        label_attrs = self.build_attrs(attrs)  # must not have 'name' attribute
        if value:
            label_attrs['value'] = self.model.objects.get(id=value)
        if not 'id' in self.attrs:
            label_attrs['id'] = label_id

        html = u'''
        <input type="hidden" %(value_attrs)s />
        <input type="text" %(label_attrs)s />

        %(select)s

        <script type="text/javascript"><!--//
          %(js)s
        //--></script>
        ''' % {
            'value_attrs': flatatt(value_attrs),
            'label_attrs': flatatt(label_attrs),
            'select': self.render_select(value_id),
            'js': self.render_js(label_id, value_id),
        }
        return html
