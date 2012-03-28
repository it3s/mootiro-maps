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

