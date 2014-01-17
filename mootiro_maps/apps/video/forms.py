# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _


class VideosWidget(forms.Widget):
    """Video selector widget"""
    class Media:
        js = (
            'js/video/video_selector.js',)
        css = {
            'all': ('css/',)
        }

    def render(self, name, value=None, attrs=None):
        html = u"""

        <div id="video-selector">
            <div>
                <a class="button" data-toggle="modal" href="#video-modal" >
                    %(add_links)s
                </a>
                <div class="modal hide video-modal" id="video-modal">
                    <div class="modal-header">
                        <button type="button" class="close" data-dismiss="modal">×</button>
                        <h3>%(add_video_links)s</h3>
                    </div>
                    <div class="modal-body">
                        <p>
                            <div class="inline-block video-link-list">
                                <div class="add-new-video-link btn">+</div>
                                <input type="text" class="video-link" name='video_link'>
                            </div>
                        </p>
                    </div>
                    <div class="modal-footer">
                        <a href="#" class="button" id="add_videos_from_links">
                            %(add)s
                        </a>
                        <a href="#" class="btn" data-dismiss="modal">
                            %(cancel)s
                        </a>

                    </div>
                </div>

                <div class="modal hide title-modal" id="title-modal">
                    <div class="modal-header">
                        <button type="button" class="close" data-dismiss="modal">×</button>
                        <h3>%(enter_title)s</h3>
                    </div>
                    <div class="modal-body">
                        <p>
                            <div>
                                <img src="" alt="img" id="video-title-modal">
                            </div>
                            <div>
                                <input type="text" name="video_title" id="id_title" data-video-id="">
                                <textarea rows=4 name="video_description" id="id_description" data-video-id=""></textarea>
                            </div>
                        </p>
                    </div>
                    <div class="modal-footer">
                        <a href="#" class="button" id="save-title">
                            %(ok)s
                        </a>
                        <a href="#" class="btn" data-dismiss="modal">
                            %(cancel)s
                        </a>
                        <a href="#" class="btn btn-danger" id="delete-video" data-video-id="">
                            %(delete)s
                        </a>

                    </div>
                </div>


            </div>

            <div id="videolist"></div>

            <div>
                <input type="hidden" id="id_videos_list" name="%(name)s" >
            </div>

        </div>
        """ % {
            'add_videos': _('Add videos'),
            'add_links': _('Add videos'),
            'add_video_links': _('Add video links'),
            'cancel': _('Cancel'),
            'add': _('Add'),
            'ok': _('Ok'),
            'enter_title': _('Edit video details'),
            'name': name,
            'delete': _('Delete'),
            'or': _('or')
        }
        return html

class VideosField(forms.CharField):
    widget = VideosWidget
