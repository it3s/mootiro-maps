from django.conf.urls.defaults import *
from fileupload.views import FileCreateView, FileDeleteView, upload_poc, upload_poc_form

urlpatterns = patterns('',
    (r'^new/$', FileCreateView.as_view(), {}, 'upload-new'),
    (r'^delete/(?P<pk>\d+)$', FileDeleteView.as_view(), {}, 'upload-delete'),

    url(r'^poc/$', upload_poc, name='upload_poc'),
    url(r'^poc/form/$', upload_poc_form, name='upload_poc_form'),
)
