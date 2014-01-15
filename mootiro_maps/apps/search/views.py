# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging
import requests
from annoying.decorators import ajax_request, render_to
from main.utils import create_geojson, get_model_from_table_ref
from .utils import search_by_term

logger = logging.getLogger(__name__)


def _has_geojson(obj):
    geometry = getattr(obj, 'geometry', '')
    return bool(geometry)


def _format_results(res):
    result = []
    for obj in res:
        id = obj['object_id']
        model = get_model_from_table_ref(obj['table_ref'])
        try:
            db_object = model.objects.get(pk=id)

            model_name = db_object.__class__.__name__.lower()
            hashlink = '{}{}'.format(model_name[0], id)
            link = db_object.view_url

            result.append({
                'id': id,
                'name': obj['name'],
                'link': link,
                'hashlink': hashlink,
                'model': model_name,
                'disabled': 'disabled' if not _has_geojson(db_object) else '',
                'geojson': create_geojson([db_object]),
            })
        except:
            # object not on DB
            pass

    return result


def _google_search(term):
    # Google search
    try:
        google_results = requests.get(
            'https://maps.googleapis.com/maps/api/place/autocomplete/json',
            params={
                'input': term,
                'sensor': 'false',
                'types': 'geocode',
                'key': 'AIzaSyDgx2Gr0QeIASfirdAUoA0jjOs80fGtBYM',
                # TODO: move to settings
            })
        results = google_results.content
    except:
        results = '{"predictions": []}'
    return results


@ajax_request
def search(request):
    logger.debug('search: {}'.format(request.POST))
    term = request.POST.get('term', '')

    raw_results = search_by_term(term)
    result = {
        'komoo': _format_results(raw_results),
        'google': _google_search(term),
    }
    return {'result': result}


@render_to('search/list.html')
def search_all(request):
    logger.debug('search_all: {}'.format(request.POST))
    term = request.GET.get('term', '')

    raw_results = search_by_term(term, size=50)
    result = _format_results(raw_results)
    return {'result': result, 'search_term': term}
