# -*- coding: utf-8 -*-
from django import template
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from fileupload.models import UploadedFile

register = template.Library()


@register.simple_tag
def upload_js():
    return """
    <script id="template-upload" type="text/x-jquery-tmpl">
        <tr class="template-upload{{if error}} ui-state-error{{/if}}">
            <td class="preview"></td>
            <td class="name">${name}</td>
            <td class="size">${sizef}</td>
            {{if error}}
                <td class="error" colspan="2">Error:
                    {{if error === 'maxFileSize'}}File is too big
                    {{else error === 'minFileSize'}}File is too small
                    {{else error === 'acceptFileTypes'}}Filetype not allowed
                    {{else error === 'maxNumberOfFiles'}}Max number of files exceeded
                    {{else}}${error}
                    {{/if}}
                </td>
            {{else}}
                <td class="progress"><div></div></td>
                <td class="start"><button>Start</button></td>
            {{/if}}
            <td class="cancel"><button>Cancel</button></td>
        </tr>
    </script>
    <script id="template-download" type="text/x-jquery-tmpl">
        <tr class="template-download{{if error}} ui-state-error{{/if}}">
            {{if error}}
                <td></td>
                <td class="name">${name}</td>
                <td class="size">${sizef}</td>
                <td class="error" colspan="2">Error:
                    {{if error === 1}}File exceeds upload_max_filesize (php.ini directive)
                    {{else error === 2}}File exceeds MAX_FILE_SIZE (HTML form directive)
                    {{else error === 3}}File was only partially uploaded
                    {{else error === 4}}No File was uploaded
                    {{else error === 5}}Missing a temporary folder
                    {{else error === 6}}Failed to write file to disk
                    {{else error === 7}}File upload stopped by extension
                    {{else error === 'maxFileSize'}}File is too big
                    {{else error === 'minFileSize'}}File is too small
                    {{else error === 'acceptFileTypes'}}Filetype not allowed
                    {{else error === 'maxNumberOfFiles'}}Max number of files exceeded
                    {{else error === 'uploadedBytes'}}Uploaded bytes exceed file size
                    {{else error === 'emptyResult'}}Empty file upload result
                    {{else}}${error}
                    {{/if}}
                </td>
            {{else}}
                <td class="preview">
                    {{if thumbnail_url}}
                        <a href="${url}" target="_blank"><img src="${thumbnail_url}"></a>
                    {{/if}}
                </td>
                <td class="name">
                    <a href="${url}"{{if thumbnail_url}} target="_blank"{{/if}}>${name}</a>
                </td>
                <td class="size">${sizef}</td>
                <td colspan="2"></td>
            {{/if}}
            <td class="delete">
                <button data-type="${delete_type}" data-url="${delete_url}">Delete</button>
            </td>
        </tr>
    </script>
    """


@register.inclusion_tag('fileupload/fileuploader_templatetag.html', takes_context=True)
def upload_widget(context, obj):
    files = UploadedFile.get_files_for(obj)
    content_type = ContentType.objects.get_for_model(obj)
    return dict(files=files, object_id=obj.id, content_type=content_type.id)


@register.simple_tag
def upload_javascript():
    return """
        {upload_js}

        <!--script src="{static_url}jquery-1.6.2.min.js"></script-->
        <script src="{static_url}jquery-ui-1.8.14.custom.min.js"></script>
        <script src="{static_url}jquery.templates/beta1/jquery.tmpl.min.js"></script>
        <script src="{static_url}jquery.iframe-transport.js"></script>
        <script src="{static_url}jquery.fileupload.js"></script>
        <script src="{static_url}jquery.fileupload-ui.js"></script>
        <script src="{static_url}application.js"></script>
    """.format(upload_js=upload_js(), static_url=settings.STATIC_URL)


@register.simple_tag
def upload_css():
    return """
    <link rel="stylesheet" href="{static_url}jqueryui/1.8.14/themes/base/jquery.ui.all.css" id="theme">
    <link rel="stylesheet" href="{static_url}jquery.fileupload-ui.css">
    <link rel="stylesheet" href="{static_url}thumbnail-scaling.css">
    """.format(static_url=settings.STATIC_URL)
