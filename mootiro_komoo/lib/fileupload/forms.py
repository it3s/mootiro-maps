# -*- coding: utf-8 -*-
from django import forms


class PluploadWidget(forms.Widget):
    """Plupload widget"""
    class Media:
        js = (
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


class FileuploadField(forms.CharField):
    widget = PluploadWidget
