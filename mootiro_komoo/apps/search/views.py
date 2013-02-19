# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
import logging
from annoying.decorators import ajax_request
from main.utils import create_geojson, get_model_from_table_ref
from .utils import search_by_term

logger = logging.getLogger(__name__)


def _has_geojson(obj):
    geometry = getattr(obj, 'geometry', '')
    return bool(geometry)


@ajax_request
def komoo_search(request):
    """
    search view for the index page.
    It uses the parameters from the 'queries' dict to perform specific
    queries on the database
    """
    logger.debug('Komoo_search: {}'.format(request.POST))
    term = request.POST.get('term', '')

    result = []
    res = search_by_term(term)
    for obj in res:
        id = obj['object_id']
        model = get_model_from_table_ref(obj['table_ref'])
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
            'has_geojson': _has_geojson(db_object),
            'geojson': create_geojson([db_object]),
        })

    # # Google search
    # google_results = requests.get(
    #     'https://maps.googleapis.com/maps/api/place/autocomplete/json',
    #     params={
    #         'input': term,
    #         'sensor': 'false',
    #         'types': 'geocode',
    #         'key': 'AIzaSyDgx2Gr0QeIASfirdAUoA0jjOs80fGtBYM',
    #         # TODO: move to settings
    #     })
    # result['google'] = google_results.content

    return {'result': result}
