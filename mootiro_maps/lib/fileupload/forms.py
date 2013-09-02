# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _
from main.utils import MooHelper
from organization.models import OrganizationCategory
import simplejson as json


class PluploadWidget(forms.Widget):
    """Plupload widget"""
    class Media:
        js = (
            'plupload/browserplus-min.js',
            'plupload/js/plupload.full.js',
            'plupload/js/jquery.plupload.queue/jquery.plupload.queue.js',
            'plupload/komoo_plupload.js',
            'plupload/js/i18n/pt-br.js',
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


class FileuploadWidget(forms.Widget):
    class Media:
        js = (
            'plupload/browserplus-min.js',
            'plupload/js/plupload.full.js',
            'plupload/komoo_plupload.js',
            # 'lib/bootstrap.min.js',
        )
        css = {
            'all': ('plupload/komoo_plupload.css',)
        }

    def render(self, name, value=None, attrs=None):
        html = u"""

        <div id="uploader">
            <div>
                <a id="pickfiles" href="#" class="button">%(select_files)s</a>
                &nbsp;%(or)s&nbsp;
                <a class="btn" data-toggle="modal" href="#file-modal" >
                    %(add_links)s
                </a>
                <div class="modal hide file-modal" id="file-modal">
                    <div class="modal-header">
                        <button type="button" class="close" data-dismiss="modal">×</button>
                        <h3>%(add_img_links)s</h3>
                    </div>
                    <div class="modal-body">
                        <p>
                            <div class="inline-block file-link-list">
                                <div class="add-new-file-link btn">+</div>
                                <input type="text" class="file-link" name='file_link'>
                            </div>
                        </p>
                    </div>
                    <div class="modal-footer">
                        <a href="#" class="button" id="add_files_from_links">
                            %(save_changes)s
                        </a>
                        <a href="#" class="btn" data-dismiss="modal">
                            %(cancel)s
                        </a>

                    </div>
                </div>

                <div class="modal hide subtitle-modal" id="subtitle-modal">
                    <div class="modal-header">
                        <button type="button" class="close" data-dismiss="modal">×</button>
                        <h3>%(enter_subtitle)s</h3>
                    </div>
                    <div class="modal-body">
                        <p>
                            <div>
                                <img src="" alt="img" id="img-subtitle-modal">
                            </div>
                            <div>
                                <input type="text" name="subtitle" id="id_subtitle" file-id="">
                            </div>
                        </p>
                    </div>
                    <div class="modal-footer">
                        <a href="#" class="button" id="save-subtitle">
                            %(save_changes)s
                        </a>
                        <a href="#" class="btn" data-dismiss="modal">
                            %(cancel)s
                        </a>
                        <a href="#" class="btn btn-danger" id="delete-file" file-id="">
                            %(delete)s
                        </a>

                    </div>
                </div>


            </div>

            <div id="filelist"></div>

            <div>
                <input type="hidden" id="id_files_ids_list" name="%(name)s" >
            </div>

        </div>
        """ % {
            'select_files': _('Select Files'),
            'add_links': _('Add Links'),
            'add_img_links': _('Add Image Links'),
            'cancel': _('Cancel'),
            'save_changes': _('Save Changes'),
            'enter_subtitle': _('Enter the subtitle for this image'),
            'name': name,
            'delete': _('Delete'),
            'or': _('or')
        }
        return html


class SingleFileUploadWidget(forms.Widget):
    class Media:
        js = (
            'plupload/browserplus-min.js',
            'plupload/js/plupload.full.js',
            'plupload/singlefile_plupload.js',
        )
        css = {
            'all': ('plupload/komoo_plupload.css',)
        }

    def render(self, name, value='', attrs=None):
        html = u"""
            <div class="div-file-wrapper">
                <div id="file-thumb"></div>
                <div id="file-uploader">
                    <a id="pick-file" href="#" class="button pick-file">%(select_file)s</a>
                </div>

                <div class="modal hide subtitle-modal" id="subtitle-modal">
                    <div class="modal-header">
                        <button type="button" class="close" data-dismiss="modal">×</button>
                        <h3>%(enter_subtitle)s</h3>
                    </div>
                    <div class="modal-body">
                        <p>
                            <div>
                                <img src="" alt="img" id="img-subtitle-modal">
                            </div>
                            <div>
                                <input type="text" name="subtitle" id="id_subtitle" file-id="">
                            </div>
                        </p>
                    </div>
                    <div class="modal-footer">
                        <a href="#" class="button" id="save-subtitle">
                            %(save_changes)s
                        </a>
                        <a href="#" class="btn" data-dismiss="modal">
                            %(cancel)s
                        </a>
                        <a href="#" class="btn btn-danger" id="delete-file" file-id="">
                            %(delete)s
                        </a>

                    </div>
                </div>
            </div>
            <div>
                <input type="hidden" class="logo-input-field" id="id_%(name)s" name="%(name)s" value="%(logo_id)s" >
            </div>

        """ % {'name': name,
               'select_file': _('Select a file'), 
               'cancel': _('Cancel'),
               'save_changes': _('Save Changes'),
               'delete': _('Delete'),
               'enter_subtitle': _('Enter the subtitle for this image'),
               'logo_id': value,
        }
        return html


class LogoWidget(forms.Widget):
    class Media:
        js = (
            'plupload/browserplus-min.js',
            'plupload/js/plupload.full.js',
            'plupload/logo_plupload.js',
        )
        css = {
            'all': ('plupload/komoo_plupload.css',)
        }

    def render(self, name, value=None, attrs=None):
        imgs_dict = json.dumps(OrganizationCategory.category_logos_dict())
        html = u"""
            <div class="div-logo-pane-wrapper">
            <div class="div-logo-pane logo-pane-left">
                <div class="logo-radio">
                    <input type="radio" name="logo_type" value="uploaded">
                    <span>Faça o upload de um logotipo</span>
                </div>
                <div id="logo-thumb"></div>
                <div id="logo-uploader">
                    <a id="picklogo" href="#" class="button">%(select_logo)s</a>
                </div>
                <div>
                    <input type="hidden" id="id_logo" name="%(name)s" >
                </div>
            </div>
            <div class="div-logo-pane logo-pane-right">
                <div class="logo-radio">
                    <input type="radio" name="logo_type" value="category" checked>
                    <span>Ou escolha uma das imagens de categoria abaixo</span>
                </div>
                <div id="logo-cat-thumbs-list"></div>
                <div>
                    <!-- input type="hidden" id="id_logo_category" name="logo_category"-->
                </div>
            </div>
            </div>
            <script type="text/javascript" charset="utf-8">
               var organization_category_images = %(img_json)s ;
            </script>

        """ % {'name': name, 'select_logo': _('Select a logo'), 'img_json': imgs_dict}
        return html


class FileuploadField(forms.CharField):
    widget = FileuploadWidget


class LogoField(forms.CharField):
    widget = LogoWidget

from django.conf import settings
from organization.models import OrganizationCategoryTranslation, OrganizationCategory

if settings.LANGUAGE_CODE == 'en-us':
    CATEGORIES = [(cat.id, cat.name) \
                for cat in OrganizationCategory.objects.all().order_by('name')]
else:
    CATEGORIES = [(cat.category_id, cat.name)\
                    for cat in OrganizationCategoryTranslation.objects.filter(
                        lang=settings.LANGUAGE_CODE).order_by('name')]


class POCForm(forms.Form):
    # files = FileuploadField()
    # title = forms.CharField()
    # categories = forms.MultipleChoiceField(required=False, choices=CATEGORIES,
    #     widget=forms.CheckboxSelectMultiple(
    #                 attrs={'class': 'org-widget-categories'}))
    # logo_choice = forms.CharField(required=False, widget=forms.HiddenInput())

    # logo = LogoField()

    single_file = FileuploadField(widget=SingleFileUploadWidget)

    def __init__(self, *a, **kw):
        self.helper = MooHelper(form_id="poc_form")
        return super(POCForm, self).__init__(*a, **kw)

