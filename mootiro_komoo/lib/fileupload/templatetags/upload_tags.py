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


@register.inclusion_tag('fileupload/image_gallery.html', takes_context=True)
def image_gallery(context, obj=None):
    images = UploadedFile.get_files_for(obj) if obj else []
    return dict(images=images)


#DEPRECATED
@register.simple_tag
def image_picker(field="logo"):
    return """
    <script type="text/javascript">
        $(function(){
            $('#files-list').prepend("" +
                "<div id='logo-advise'>Escolha uma imagem abaixo para ser o logo</div>"
            );

            if ($('#id_%(field)s').val()) {
                $('.file-entry[file-id=' + $('#id_%(field)s').val() + ']').addClass('file-entry-main');
            }

            $('.file-entry').live('click', function(){
                $('.file-entry-main').removeClass('file-entry-main');
                $(this).addClass('file-entry-main');
            });

            $('form').submit(function(evt){
                var id = $('.file-entry-main').attr('file-id');
                $('#id_%(field)s').val(id);
            })
        });

    </script>
    <style type="text/css">
        .file-entry:hover{
            background-color: rgb(64, 146, 169);
            color: #cccccc;
        }
        .file-entry:hover span{
            color: #cccccc;
        }
        .file-entry-main{
            background-color: rgb(64, 146, 169);
            color: #cccccc;
        }
        .file-entry-main span{
            color: #cccccc;
        }
        #logo-advise{
            text-align: center;
            color: #999999;
            padding: 10px;
            font-weight: bold;
        }
    </style>
    """ % {'field': field}
