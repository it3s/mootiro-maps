#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default

import json
import simplejson
import requests
import datetime
from markdown import markdown
from string import letters, digits
from random import choice
from dateutil.parser import parse as dateutil_parse
from copy import deepcopy

from django import forms
from django.http import HttpResponse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.utils.translation import ugettext_lazy as _
from django.http import Http404, HttpResponseNotAllowed
from django.core.mail import send_mail as django_send_mail
from django.conf import settings
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

try:
    from functools import wraps
except ImportError:
    def wraps(wrapped, assigned=('__module__', '__name__', '__doc__'),
              updated=('__dict__',)):
        def inner(wrapper):
            for attr in assigned:
                setattr(wrapper, attr, getattr(wrapped, attr))
            for attr in updated:
                getattr(wrapper, attr).update(getattr(wrapped, attr, {}))
            return wrapper
        return inner


def create_geojson(objects, type_='FeatureCollection', convert=True,
                   discard_empty=False):
    if type_ == 'FeatureCollection':
        geojson = {
            'type': 'FeatureCollection',
            'features': []
        }

        for obj in objects:
            type_ = obj.__class__.__name__
            if not hasattr(obj, 'geometry'):
                continue
            geometry_json = json.loads(obj.geometry.geojson)
            geometries = geometry_json['geometries']
            geometry = None

            if geometries:
                if len(geometries) == 1:
                    geometry = geometries[0]
                else:
                    geometry = {}
                    geometry_type = geometries[0]['type']
                    geometry['type'] = 'Multi{}'.format(geometry_type)
                    coord = []
                    for geom in geometries:
                        if geom['type'] == geometry_type:
                            coord.append(geom['coordinates'])
                    geometry['coordinates'] = coord

            if discard_empty and not geometry:
                return {}

            name = getattr(obj, 'name', getattr(obj, 'title', ''))
            last_update = obj.last_update.isoformat(b' ') if getattr(obj,
                    'last_update', None) else ''

            feature = {
                'type': 'Feature',
                'geometry': geometry,
                'properties': {
                    'type': type_,
                    'name': name,
                    'id': obj.id,
                    'lastUpdate': last_update
                }
            }
            if hasattr(obj, 'categories'):
                feature['properties']['categories'] = [
                        {'name': c.name, 'image': c.image}
                        for c in obj.categories.all()]
            if hasattr(obj, 'population'):
                feature['properties']['population'] = obj.population

            geojson['features'].append(feature)

    if convert:
        return json.dumps(geojson)

    return geojson


class MooHelper(FormHelper):
    def __init__(self, form_id=None, *a, **kw):
        r = super(MooHelper, self).__init__(*a, **kw)
        if form_id:
            self.form_id = form_id
        self.add_input(Submit('submit', _('Submit'), css_class='button'))
        return r


def paginated_query(query, request=None, page=None, size=None):
    """
    Do the boring/repetitive pagination routine.
    Expects a request with page and size attributes
    params:
        query: any queryset objects
        request:  a django HttpRequest (GET)
           page: page attr on request.GET (default: 1)
           size: size attr on request.GET (default: 10)
        size: size of each page
        page: number of the current page
    """
    page = page or request.GET.get('page', '')
    size = size or request.GET.get('size', 10)

    paginator = Paginator(query, size)
    try:
        _paginated_query = paginator.page(page)
    except PageNotAnInteger:  # If page is not an integer, deliver first page.
        _paginated_query = paginator.page(1)
    except EmptyPage:  # If page is out of range, deliver last page
        _paginated_query = paginator.page(paginator.num_pages)
    return _paginated_query


date_order_map = {
    'desc': '-',
    'asc': ''
}


def sorted_query(query_set, sort_fields, request, default_order='name'):
    """
    Used for handle listing sorters
    params:
        query_set: any query set object or manager
        request: the HttpRequest obejct
    """
    query_set = query_set.all()
    sort_order = {k: i for i, k in enumerate(sort_fields)}
    sorters = request.GET.get('sorters', '')
    if sorters:
        sorters = sorted(sorters.split(','), key=lambda val: sort_order[val])

    for i, sorter in enumerate(sorters[:]):
        if 'date' in sorter:
            date_order = request.GET.get(sorter, '-')
            sorters[i] = date_order_map[date_order] + sorter

    if sorters:
        return query_set.order_by(*sorters)
    else:
        return query_set.order_by(default_order)


def filtered_query(query_set, request):
    filters = request.GET.get('filters', '')
    for f in filters.split(','):
        if f == 'tags':
            request.encoding = 'latin-1'
            tags = request.GET.get('tags', '')

            if tags:
                tags = tags.split(',')
                for tag in tags:
                    query_set = query_set.filter(tags__name=tag)
        if f == 'community':
            community = request.GET.get('community', '')
            if community:
                query_set = query_set.filter(community=community)
        if f == 'need_categories':
            need_categories = request.GET.get('need_categories', '')
            if need_categories:
                need_categories = need_categories.split(',')
                for nc in need_categories:
                    query_set = query_set.filter(categories=nc)
        if f == 'target_audiences':
            request.encoding = 'latin-1'
            target_audiences = request.GET.get('target_audiences', '')
            if target_audiences:
                target_audiences = target_audiences.split(',')
                for ta in target_audiences:
                    query_set = query_set.filter(target_audiences__name=ta)

    return query_set


def templatetag_args_parser(*args):
    """
    Keyword-arguments like function parser. Designed to be used in templatetags
    Usage:
    ```
        def mytemplatetag(..., arg1='', arg2='', arg3=''):
          parsed_args = templatetag_args_parser(arg1, arg2, arg3)

          label = parsed_args.get('label', 'Default')
          use_border = parsed_args.get('use_border', False)
          zoom = parsed_args.get('zoom', 16)
    ```

    And in the template...
      {% mytemplatetag 'zoom=12' 'label=Your name' %}

    """
    parsed_args = {}
    for arg in args:
        if arg:
            a = arg.split('=')
            parsed_args[a[0]] = a[1]
    return parsed_args


def clean_autocomplete_field(field_data, model):
    try:
        if not field_data or field_data == 'None':
            return model()
        else:
            return model.objects.get(pk=field_data)
    except:
        raise forms.ValidationError(_('invalid field data'))


def render_markup(text):
    return markdown(text, safe_mode=True) if text else ''


def send_mail(title='', message='',
              sender='MootiroMaps <no-reply@it3s.mailgun.org>', receivers=[],
              html=False):
    '''
    function for sending mails. If we are on debug (development) se will be
    sent by django mailer else will use the mailgun api.
    mailer.
    '''
    if settings.DEBUG and not html:
        django_send_mail(title, message, sender, receivers,
                            fail_silently=False)
    else:
        data = {
            'from': 'MootiroMaps <no-reply@it3s.mailgun.org>',
            'to': receivers,
            'subject': title,
        }
        if html:
            data['html'] = message
        else:
            data['text'] = message

        requests.post(
            settings.MAILGUN_API_URL,
            auth=('api', settings.MAILGUN_API_KEY),
            data=data
        )


def get_handler_method(request_handler, http_method):
    """Utility function for the Resource Class dispacther."""
    try:
        handler_method = getattr(request_handler, http_method.lower())
        if callable(handler_method):
            return handler_method
    except AttributeError:
        pass


class ResourceHandler:
    """
    Base class for REST-like resources.
    usage:

      on views.py
          ```
              class SomeResource(ResourceHandler):

                def get(self, request, document_id):
                  # your view code for GET requests go here

                def post(self, request, document_id):
                  # your viewcode for POST request go here
            ```

      on urls.py
        url('^my_resource/$', views.SomeResource.dispatch, name='resource')
    """
    http_methods = ['GET', 'POST', 'HEAD', 'PUT', 'DELETE', 'OPTIONS', 'TRACE']

    @classmethod
    def dispatch(cls, request, *args, **kwargs):
        request_handler = cls()

        if request.method in cls.http_methods:
            handler_method = get_handler_method(request_handler,
                                                request.method)
            if handler_method:
                return handler_method(request, *args, **kwargs)

        methods = [method for method in cls.http_methods if get_handler_method(
                                            request_handler, method)]
        if len(methods) > 0:
            # http 405: method not allowed
            return HttpResponseNotAllowed(methods)
        else:
            raise Http404


def randstr(l=10):
    chars = letters + digits
    s = ''
    for i in range(l):
        s = s + choice(chars)
    return s


def get_filter_params(request):
    filtered = bool(request.GET.get('filters', None))
    request.encoding = 'latin-1'
    filter_params = request.GET
    return (filtered, filter_params)

# ======================================================


def datetime_to_iso(datetime_obj):
    """ parses a python datetime object to a ISO-8601 string """
    if datetime_obj is None:
        return None
    return datetime_obj.isoformat()


def iso_to_datetime(iso_string):
    """ parses a ISO-8601 string into a python datetime object """
    if iso_string is None:
        return None
    return dateutil_parse(iso_string)


def parse_accept_header(request):
    """
    Parse the Accept header *accept*, returning a list with pairs of
    (media_type, q_value), ordered by q values.
    ref: http://djangosnippets.org/snippets/1042/
    """
    accept = request.META.get('HTTP_ACCEPT', '')
    result = []
    for media_range in accept.split(','):
        parts = media_range.split(';')
        media_type = parts.pop(0)
        media_params = []
        q = 1.0
        for part in parts:
            (key, value) = part.lstrip().split('=', 1)
            if key == 'q':
                q = float(value)
            else:
                media_params.append((key, value))
        result.append((media_type, tuple(media_params), q))
    result.sort(lambda x, y: -cmp(x[2], y[2]))
    return result


class ResourceHandler:
    """
    Base class for REST-like resources.
    usage:

      on views.py
      ```
      class SomeResource(ResourceHandler):

        def get(self, request, document_id):
          # your view code for GET requests go here

        def post(self, request, document_id):
          # your viewcode for POST request go here
      ```
      on urls.py
        url('^my_resource/$', views.SomeResource.dispatch, name='resource')
    """
    http_methods = ['GET', 'POST', 'HEAD', 'PUT', 'DELETE', 'OPTIONS', 'TRACE']

    @classmethod
    def as_view(cls, *args, **kwargs):
        # Keeps compatibility with Django's class-view interface
        return cls.dispatch

    def _get_handler_method(self, request_handler, http_method):
        """ Utility function for the Resource Class dispacther."""
        try:
            handler_method = getattr(request_handler, http_method.lower())
            if callable(handler_method):
                return handler_method
        except AttributeError:
            pass

    @classmethod
    def dispatch(cls, request, *args, **kwargs):
        req_handler = cls()

        req_handler.accept = parse_accept_header(request)
        req_handler.accept_type = req_handler.accept[0][0]

        if request.method in cls.http_methods:
            handler_method = req_handler._get_handler_method(req_handler,
                                                             request.method)
            if handler_method:
                return handler_method(request, *args, **kwargs)

        methods = [method for method in req_handler.http_methods if
                req_handler._get_handler_method(req_handler, method)]
        if len(methods) > 0:
            # http 405: method not allowed
            return HttpResponseNotAllowed(methods)
        else:
            raise Http404


def filter_dict(data, keys):
    """ remove unnecessary data """
    data = deepcopy(data)
    for k in keys:
        if k in data:
            del data[k]
    return data


def get_fields_to_show(request, default=['all']):
    data = request.GET.get('fields', None)
    return data.split(',') if data else default


def get_json_data(request):
    """
    get raw json data from request.
    Usefull for requests from Backbone.sync
    """
    return simplejson.loads(request.raw_post_data)


def _to_json_default(obj):
    """
    Converts non default objects to json
    usage:
        simplejson.dumps(data, default=to_json)
    """

    # Geometries
    if getattr(obj, 'geojson', None):
        return simplejson.dumps(obj.geojson)

    # Datetime
    if isinstance(obj, datetime.datetime):
        return datetime_to_iso(obj)

    try:
        return obj.id
    except Exception:
        raise TypeError(repr(obj) + ' is not JSON serializable')


def to_json(data):
    return simplejson.dumps(data, default=_to_json_default)


class JsonResponse(HttpResponse):
    """
    Creates a Json Response. The Http status code can be changed.
    usage:
        ```
            def my_view(request):
                # some code
                return JsonResponse(my_data_dict)
            def my_other_view(request):
                # some code
                return JsonResponse(my_errors_dict, status_code=400)
        ```
    """
    def __init__(self, data={}, status_code=None):
        content = to_json(data)
        super(JsonResponse, self).__init__(content=content,
                    mimetype='application/json')
        if status_code:
            self.status_code = status_code


class JsonResponseError(JsonResponse):
    """ Json Response for errors """
    def __init__(self, error={}, status_code=400):
        super(JsonResponseError, self).__init__(
                {'errors': error}, status_code=status_code)


class JsonResponseNotFound(JsonResponseError):
    """ Json Response for 404 Not Found error """
    def __init__(self, msg=''):
        err = 'Not found'
        super(JsonResponseNotFound, self).__init__(
                err if not msg else '{}: {}'.format(err, msg),
                status_code=404)


def build_obj_from_dict(obj, data, keys=[], date_keys=[]):
    """ utility function for being use with .from_dict() methods """
    for key, val in data.iteritems():
        if key in keys:
            if key in date_keys and isinstance(val, basestring):
                setattr(obj, key, iso_to_datetime(val))
            else:
                setattr(obj, key, val)


def get_model_from_table_ref(table_ref):
    """
    given a table_ref like 'app_label.class_name', return the refered model
    """
    module_name, model_name = table_ref.split('.')
    module = __import__(module_name)
    models = getattr(module, 'models')
    model = getattr(models, model_name)
    return model

