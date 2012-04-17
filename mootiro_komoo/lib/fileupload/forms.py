# -*- coding: utf-8 -*-
from django import forms


class FileuploadInputWidget(forms.TextInput):

    def render(self, name, value=None, attrs=None):
        html = u"""
        <input type="hidden" name="%(name)s" id="id_%(name)s" />

        <script type="text/javascript" ><!--//
            var node;
            var id_files = $('#id_%(name)s')

            for(node = id_files; ! node.is('form'); node = node.parent());

            /* node is the containing form now*/
            node.submit(function(evt){

                id_files.val(getFilesIdList().join('|'));

                return true;
            });
        //--></script>
        """ % dict(name=name)

        return html


class FileuploadField(forms.CharField):
    widget = FileuploadInputWidget


class PluploadWidget(forms.Widget):
    """Plupload widget"""
    class Media:
        js = (
            # 'lib/jquery-1.7.1.js',
            'plupload/browserplus-min.js',
            'plupload/js/plupload.full.js',
            'plupload/js/jquery.plupload.queue/jquery.plupload.queue.js',
            'plupload/komoo_plupload.js',
        )
        css = {
            'all': ('plupload/komoo_plupload.css',)
        }

    def render(self, name, value=None, attrs=None):
        html = u"""
            <div id="uploader">
                <p>You browser doesn't have Flash, Silverlight, Gears, BrowserPlus or HTML5 support.</p>
            </div>
            <div>
                <input type="hidden" id="id_files_ids_list" name="%(name)s" >
            </div>

            <div id="files-list"></div>
        """ % {'name': name}
        return html
