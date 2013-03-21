# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import Highlight, HighlightSection


class HighlightAdmin(admin.ModelAdmin):
    list_display =  ['section', 'object_type', 'object_id', 'section_order', 'is_active']
    list_editable = ['section', 'section_order', 'is_active']
    list_display_links = ['object_type', 'object_id']
    ordering = ['section']
    save_as = True


class HighlightSectionAdmin(admin.ModelAdmin):
    list_display =  ['page_name', 'name', 'page_order', 'is_active']
    list_editable = ['page_name', 'page_order', 'is_active']
    list_display_links = ['name']
    ordering = ['page_name']


admin.site.register(Highlight, HighlightAdmin)
admin.site.register(HighlightSection, HighlightSectionAdmin)
