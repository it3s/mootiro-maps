from django.conf.urls.defaults import *
from fileupload.views import *

urlpatterns = patterns('',
    (r'^new/$', FileCreateView.as_view(), {}, 'upload-new'),
    (r'^delete/(?P<pk>\d+)$', FileDeleteView.as_view(), {}, 'upload-delete'),

    (r'^poc/$', uploader_poc),

    (r'^file_info/$', file_info),
    (r'^add_from_link/$', save_file_from_link),
    (r'^save_subtitle/$', save_subtitle),

)
