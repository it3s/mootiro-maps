# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging

from django import forms
from django.utils.translation import ugettext_lazy as _

from markitup.widgets import MarkItUpWidget
from fileupload.forms import FileuploadField
from ajaxforms import AjaxModelForm

from main.utils import MooHelper
from main.widgets import TaggitWidget
from .models import Project

logger = logging.getLogger(__name__)


class FormProject(AjaxModelForm):
    description = forms.CharField(widget=MarkItUpWidget())
    tags = forms.Field(required=False, widget=TaggitWidget(
        autocomplete_url="/project/search_tags/"))
    logo = FileuploadField(required=False)

    class Meta:
        model = Project
        fields= ('name', 'description', 'tags', 'logo', 'id')

    _field_labels = {
        'name': _('Name'),
        'description': _('Description'),
        'tags': _('Tags'),
        'logo': _('Logo'),
    }

    def __init__(self, *a, **kw):
        self.helper = MooHelper(form_id='form_project')
        return super(FormProject, self).__init__(*a, **kw)



