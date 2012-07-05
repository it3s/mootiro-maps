#coding: utf-8
import json
from django import template
from django.conf import settings

from komoo_map.models import get_models_json
register = template.Library()


def _parse_args(*args):
    parsed_args = {}
    for arg in args:
        if arg:
            a = arg.split('=')
            parsed_args[a[0]] = a[1]
    return parsed_args


@register.inclusion_tag('komoo_map/komoo_map_tooltip_templatetag.html')
def komoo_map_tooltip():
    pass


@register.inclusion_tag('komoo_map/komoo_map_templatetag.html',
        takes_context=True)
def komoo_map(context, geojson={}, arg1='', arg2='', arg3='', arg4='',
        arg5='', arg6='', arg7='', arg8=''):
    """
    The syntax:
        {% komoo_map <geojson> [type] [<width>] [<height>] [<zoom>] [panel] [ajax] [lazy] [edit_button] %}
    """
    parsed_args = _parse_args(arg1, arg2, arg3, arg4, arg5, arg6, arg7, arg8)
    type = parsed_args.get('type', 'main')
    width = parsed_args.get('width', '200')
    height = parsed_args.get('height', '200')
    zoom = parsed_args.get('zoom', 16)
    panel = parsed_args.get('panel',
            'True' if not type in ('preview') else 'False'
        ).lower() != 'false'
    ajax = parsed_args.get('ajax', 'True').lower() != 'false'
    lazy = parsed_args.get('lazy', 'False').lower() != 'false'
    edit_button = parsed_args.get('edit_button', 'False').lower() != 'false'

    editable = type in ('main', 'editor')
    if geojson:
        geojson_dict = json.loads(geojson);
        for feature in geojson_dict.get('features', []):
            if 'properties' in feature:
                feature['properties']['alwaysVisible'] = True
        geojson = json.dumps(geojson_dict)


    if not width.endswith('%') and not width.endswith('px'):
        width = width + 'px'
    if not height.endswith('%') and not height.endswith('px'):
        height = height + 'px'

    if getattr(settings, 'KOMOO_DISABLE_MAP', False):
        type = 'disabled'

    return dict(type=type, width=width, height=height, zoom=zoom,
            panel=panel, lazy=lazy, geojson=geojson, edit_button=edit_button,
            ajax=ajax, editable=editable, feature_types_json=get_models_json(),
            STATIC_URL=settings.STATIC_URL, LANGUAGE_CODE=settings.LANGUAGE_CODE)
