# -*- coding: utf-8 -*-
from django import template
from django.contrib.contenttypes.models import ContentType
from fileupload.models import UploadedFile

register = template.Library()


@register.inclusion_tag('fileupload/plupload_edit_tag.html', takes_context=True)
def load_files(context, obj=None):
    if obj:
        files = UploadedFile.get_files_for(obj)
        object_id = obj.id
        content_type = ContentType.objects.get_for_model(obj).id
    else:
        files = []
        object_id = ''
        content_type = ''
    return dict(files=files, object_id=object_id, content_type=content_type)
