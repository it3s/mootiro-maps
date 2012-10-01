#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django.conf.urls.defaults import patterns, include, url
from django.views.i18n import javascript_catalog
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# Some URL fragments to be reused throughout the application
COMMUNITY_SLUG = r'(?P<community_slug>[a-zA-Z0-9-]+)'
NEED_SLUG = r'(?P<need_slug>[a-zA-Z0-9-]+)'
PROPOSAL_NUMBER = r'(?P<proposal_number>\d+)'
ORGANIZATION_SLUG = r'(?P<organization_slug>[a-zA-Z0-9-]+)'
RESOURCE_ID = r'(?P<resource_id>\d+)'
INVESTMENT_SLUG = r'(?P<investment_slug>[a-zA-Z0-9-]+)'
PROJECT_SLUG = r'(?P<project_slug>[a-zA-Z0-9-]+)'
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
    return regex.replace('COMMUNITY_SLUG', COMMUNITY_SLUG) \
                .replace('NEED_SLUG', NEED_SLUG) \
                .replace('PROPOSAL_NUMBER', PROPOSAL_NUMBER) \
                .replace('ORGANIZATION_SLUG', ORGANIZATION_SLUG) \
                .replace('RESOURCE_ID', RESOURCE_ID) \
                .replace('INVESTMENT_SLUG', INVESTMENT_SLUG) \
                .replace('PROJECT_SLUG', PROJECT_SLUG) \
                .replace('SLUG', SLUG) \
                .replace('ID', ID)


def multiurls(prefixes, view_defs):
    """Generates a list of django urls from the cartesian product of prefixes
    and suffixes.
    Usage example:
        multirurls(
            prefixes=[r'^COMMUNITY_SLUG/', r''],
            view_defs=[
                (r'need/NEED_SLUG', 'view', 'view_need'),
                (r'need/new', 'edit', 'new_need'),
                (r'need/NEED_SLUG/edit', 'edit', 'edit_need')
            ]
        )
    """
    urls = []
    for p in prefixes:
        for vd in view_defs:
            regexp = prepare_regex(p + vd[0])
            urls.append(url(regexp, vd[1], name=vd[2]))
    return urls


# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^jsi18n/$', javascript_catalog, js_info_dict, name='javascript_catalog'),
    # admin stuff
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),

    # user and CAS urls
    url(r'^user/', include('user_cas.urls')),
    url(r'^login/cas?$', 'django_cas.views.login'),
    url(r'', include('social_auth.urls')),

    url(r'^markitup/', include('markitup.urls')),
    url(r'^upload/', include('fileupload.urls')),
    url(r'^lookups/', include('ajax_select.urls')),

    url(r'^$', 'update.views.frontpage', name='frontpage'),

    url(r'', include('need.urls')),
    url(r'', include('proposal.urls')),
    url(r'', include('main.urls')),
    url(r'^comments/', include('komoo_comments.urls')),
    url(r'^vote/', include('vote.urls')),
    url(r'', include('komoo_resource.urls')),
    url(r'', include('organization.urls')),
    url(r'', include('investment.urls')),
    url(r'', include('moderation.urls')),
    url(r'', include('update.urls')),
    url(r'', include('hotsite.urls')),
    url(r'', include('komoo_project.urls')),
    url(r'', include('discussion.urls')),
    url(r'^map_info/', include('komoo_map.urls')),
    url(r'^about/', include('hotsite.urls')),
    url(r'^about', 'hotsite.views.root'),
    url(r'^signatures/', include('signatures.urls')),

    # Community URLs go last because one of them can match anything
    url(r'', include('community.urls')),
)

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()  # this servers static files and media files.
    #in case media is not served correctly
    urlpatterns += patterns('',
        url(r'^' + settings.MEDIA_URL.lstrip('/') + r'(?P<path>.*)$',
            'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, }),
    )
