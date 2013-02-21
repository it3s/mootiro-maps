#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django.conf.urls.defaults import patterns, include, url
from django.views.i18n import javascript_catalog
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from django.contrib import admin
admin.autodiscover()

# Some URL fragments to be reused throughout the application
SLUG = r'(?P<slug>[a-zA-Z0-9-]+)'
ID = r'(?P<id>\d+)'

handler500 = 'main.views.custom_500'
handler404 = 'main.views.custom_404'

js_info_dict = {
    'packages': (
        'komoo_map',
        )
}


def prepare_regex(regex):
    return regex.replace('SLUG', SLUG).replace('ID', ID)

urlpatterns = patterns('',
    # admin stuff
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),

    # user
    url(r'^user/', include('authentication.urls')),

    # 3rd party apps
    url(r'^markitup/', include('markitup.urls')),
    url(r'^upload/', include('fileupload.urls')),
    url(r'^lookups/', include('ajax_select.urls')),
    url(r'^jsi18n/$', javascript_catalog, js_info_dict,
        name='javascript_catalog'),

    # root
    url(r'^$', 'main.views.root', name='root'),

    # unprefixed urls
    #url(r'', include('hotsite.urls')),
    url(r'', include('main.urls')),
    url(r'', include('search.urls')),

    # prefixed apps urls
    url(r'^need/', include('need.urls')),
    url(r'^proposal/', include('proposal.urls')),
    url(r'^comments/', include('komoo_comments.urls')),
    url(r'^resource/', include('komoo_resource.urls')),
    url(r'^organization/', include('organization.urls')),
    url(r'^investment/', include('investment.urls')),
    url(r'^moderation/', include('moderation.urls')),
    url(r'^project/', include('komoo_project.urls')),
    url(r'^discussion/', include('discussion.urls')),
    url(r'^map_info/', include('komoo_map.urls')),
    url(r'^about/', include('hotsite.urls')),
    url(r'^signatures/', include('signatures.urls')),
    url(r'^community/', include('community.urls')),
    url(r'^update/', include('update.urls')),
    url(r'^importsheet/', include('importsheet.urls')),
)

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += patterns('',
        url(r'^' + settings.MEDIA_URL.lstrip('/') + r'(?P<path>.*)$',
            'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT, }),
    )
