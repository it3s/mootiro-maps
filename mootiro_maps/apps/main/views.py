#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default

import logging
from smtplib import SMTPException

from django.contrib.gis.geos import Polygon, Point
from django.contrib.gis.measure import Distance
from django.template import loader, Context
from django.db.models import Q
from django.db.models.loading import cache
from django.http import (HttpResponse, HttpResponseNotFound,
                         HttpResponseServerError, HttpResponseBadRequest,
                         HttpResponseRedirect)
from django.core.mail import mail_admins
from django.utils import translation
from django.utils.translation import ugettext as _
from django.shortcuts import redirect
from django.conf import settings

from annoying.decorators import render_to, ajax_request
from annoying.functions import get_object_or_None

from authentication.models import User
from community.models import Community
from need.models import Need
from proposal.models import Proposal
from organization.models import Organization
from komoo_resource.models import Resource
from investment.models import Investment
from komoo_project.models import Project
from main.utils import create_geojson, ResourceHandler, to_json
from update.models import Update, News

logger = logging.getLogger(__name__)


# Association between the code used to create permalinks
# and the internal model.
ENTITY_MODEL = {
    'c': Community,
    'n': Need,
    'p': Proposal,
    'o': Organization,
    'r': Resource,
    'i': Investment,
    'j': Project,
    'u': User,
}
# The reverse association.
ENTITY_MODEL_REV = {v: k for k, v in ENTITY_MODEL.items()}


@render_to('main/map.html')
def map(request):
    """Display the main map getting data via ajax."""
    return dict(geojson={})


@render_to('main/about.html')
def about(request):
    """Display a static page containing usefull info about the service."""
    return dict()


@render_to('main/use_cases.html')
def use_cases(request):
    """Display a static page containing example of how this application
    can be usefull."""
    return dict()


@render_to('main/root.html')
def root(request):
    """The front page."""
    updates = Update.objects.all().order_by("-date")[:4]
    news = News.objects.order_by("-date")[:4]
    return dict(updates=updates, news=news)


def _fetch_geo_objects(query, zoom,
                       models=[User, Community, Need, Resource, Organization],
                       project=None):
    """Helper function to create a geojson compatible dict.

    Use some parameters to filter the data that will be returned.

    Params:
        query: a Django model query. Can use Q class to use complex queries.
        models: a list of models to filter using the query passed. (Default:
            [User, Community, Need, Resource, Organization])
        project: a project instance or project id used to restrict the filtered
            objects. If passed, only objects related with this project will
             be returned.

    Returns a dictionary.

    """
    ret = {}
    if not project:
        for model in models:
            ret[model.__name__] = model.objects.filter(query)
    else:
        if isinstance(project, Project):
            proj = project
        else:
            proj = get_object_or_None(Project, pk=project)

        if proj:
            ret['all'] = proj.filter_related_items(query, models)
    return ret


from django.views.decorators.cache import cache_page
@cache_page(54000)
def get_geojson(request):
    """View used by the map javascript to fetch geojson data for each map tile.

    This view receives some parameters via GET request and returns a geojson
    reponse.

    Params:
        bounds: string of the form "lat_lo,lng_lo,lat_hi,lng_hi", where "lo"
            corresponds to the southwest corner of the bounding box,
            while "hi" corresponds to the northeast corner of that box.
        zoom: the map zoom level.
        models: a list of model to filter, separated by comma, of the form
            "app_name.ModelNamel".
        project - the id of the the project with which the filtered objects
            should have ralations. (Optional)

    """
    bounds = request.GET.get('bounds', None)
    zoom = int(request.GET.get('zoom', 13))
    models = request.GET.get('models', '')
    project = request.GET.get('project', None)

    if not bounds and not project:
        return HttpResponseBadRequest(to_json({'error': 'Invalid query'}),
                                      mimetype="application/x-javascript")

    if bounds:
        x1, y2, x2, y1 = [float(i) for i in bounds.split(',')]
        polygon = Polygon(((x1, y1), (x1, y2), (x2, y2), (x2, y1), (x1, y1)))

        intersects_polygon = (Q(points__intersects=polygon) |
                              Q(lines__intersects=polygon) |
                              Q(polys__intersects=polygon))
    else:
        intersects_polygon = Q()

    models = [cache.get_model(*m.split('.')) for m in models.split(',') if m]
    d = _fetch_geo_objects(intersects_polygon, zoom, models, project)
    l = []
    for objs in d.values():
        l.extend(objs)
    geojson = create_geojson(l)
    return HttpResponse(to_json(geojson),
                        mimetype="application/x-javascript")


@render_to("main/filter_results.html")
def radial_search(request):
    """View used to search by objects within a specif circular area.

    This view receives parameters from GET request and returns a html page
    containing the result.

    Request params:
        center: the center coordinate of the circle.
        radius: the circle radius.

    """
    center = Point(*[float(i) for i in request.GET['center'].split(',')])
    radius = Distance(m=float(request.GET['radius']))

    distance_query = (Q(points__distance_lte=(center, radius)) |
                      Q(lines__distance_lte=(center, radius)) |
                      Q(polys__distance_lte=(center, radius)))

    objs = _fetch_geo_objects(distance_query, 100)
    d = {}
    if 'communities' in request.GET:
        d['Community'] = objs['Community']
    if 'needs' in request.GET:
        need_categories = request.GET['need_categories'].split(',')
        d['Need'] = []
        for n in objs['Need']:
            if [c for c in n.categories.all() if str(c.id) in need_categories]:
                d['Need'].append(n)
    if 'organizations' in request.GET:
        d['Organization'] = objs['Organization']
    if 'resources' in request.GET:
        d['Resource'] = objs['Resource']

    return d


@ajax_request
def send_error_report(request):
    """ View used by users to send an error report when a 404 or a 500 error
    page is displayed.

    This view receives 3 parameters via POST request and returns a json with
    a success or error feedback.

    POST params:
        message: a message written by the user describing what occurred.
        info: information about the error collected automatically.
        url: in which page the error occurred.

    """
    user = request.user
    user_message = request.POST.get('message', '')
    info = request.POST.get('info', '')
    url = request.POST.get('url', '')

    message = _("""
Url: {0}
Reporter: {1} (id: {2}, email: {3})
Info: {4}
Message: {5}
    """).format(url, user, user.id, user.email, info, user_message)

    try:
        mail_admins(_('Error report'), message, fail_silently=False)
        status = 'sent'
        success = 'true'
    except SMTPException:
        status = 'failed'
        success = 'false'
    finally:
        return {'status': status, 'success': success}


@render_to('404.html')
def test_404(request):
    """View used just to test the 404 error page design."""
    return {}


@render_to('500.html')
def test_500(request):
    """View used just to test the 500 error page design."""
    return {}


def custom_404(request):
    """View that display the real 404 error page."""
    t = loader.get_template('404.html')
    c = Context({'request_path': request.path, 'STATIC_URL': '/static/'})
    return HttpResponseNotFound(t.render(c))


def custom_500(request):
    """View that display the real 500 error page."""
    t = loader.get_template('500.html')
    c = Context({})
    return HttpResponseServerError(t.render(c))


@render_to('not_anymore.html')
def permalink(request, identifier=''):
    """View that receives a permalink and redirects to the real url."""
    url = 'root'
    if identifier:
        entity, id_ = identifier[0], identifier[1:]
        obj = get_object_or_None(ENTITY_MODEL[entity], pk=id_)
        if not obj:
            return {}
        url = getattr(obj, 'view_url', '/')
    return redirect(url)


@ajax_request
def get_geojson_from_hashlink(request):
    """View that returns geojson using the permalink hash code to identify
    the correct object."""
    hashlink = request.GET.get('hashlink', '')
    if hashlink:
        obj = ENTITY_MODEL[hashlink[0]].objects.get(pk=hashlink[1:])
        geojson = create_geojson([obj])
    else:
        geojson = {}

    return {'geojson': geojson}


def set_language(request):
    next_ = request.REQUEST.get('next', None)
    if not next_:
        next_ = request.META.get('HTTP_REFERER', None)
    if not next_:
        next_ = '/'
    response = HttpResponseRedirect(next_)
    lang_code = (request.GET.get('language', None) or
                 request.POST.get('language', None))
    if lang_code and translation.check_for_language(lang_code):
        if hasattr(request, 'session'):
            request.session['django_language'] = lang_code
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code)
        translation.activate(lang_code)
        if not request.user.is_anonymous():
            request.user.set_language(lang_code)
            request.user.save()
    return response


if settings.TESTING:
    class TestResourceHandler(ResourceHandler):
        """This is only a dummy handler used for testing"""
        def get(self, request):
            return HttpResponse('Resource::GET')

        def post(self, request):
            return HttpResponse('Resource::POST')

        def put(self, request):
            return HttpResponse('Resource::PUT')

        def delete(self, request):
            return HttpResponse('Resource::DELETE')
