# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import Highlight, HighlightSection


class HighlightSectionAdmin(admin.ModelAdmin):
    list_display =  ['page_name', 'name', 'page_order', 'is_active', 'link_url', 'hide_short_description']
    list_editable = ['page_name', 'page_order', 'is_active', 'hide_short_description']
    list_display_links = ['name']
    ordering = ['page_name']


class HighlightAdmin(admin.ModelAdmin):
    list_display =  ['section', 'section_order', 'is_active',
                     'object_type', 'object_id', 'name']
    list_editable = ['section', 'section_order', 'is_active',
                     'object_type', 'object_id']
    list_display_links = ['name']
    ordering = ['section']
    save_as = True


admin.site.register(Highlight, HighlightAdmin)
admin.site.register(HighlightSection, HighlightSectionAdmin)
