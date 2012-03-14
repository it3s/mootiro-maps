#coding: utf-8
from django import template
from django.conf import settings
register = template.Library()


def _parse_args(*args):
    parsed_args = {}
    for arg in args:
        if arg:
            a = arg.split('=')
            parsed_args[a[0]] = a[1]
    return parsed_args


@register.inclusion_tag('komoo_map/editor.html', takes_context=True)
def komoo_map(context, geojson={}, arg1='', arg2='', arg3='', arg4=''):
    """
    The syntax:
        {% komoo_map <geojson> [<editable>] [<width>] [<height>] [<zoom>] %}
    """
    parsed_args = _parse_args(arg1, arg2, arg3, arg4)
    editable = parsed_args.get('editable', False)
    width = parsed_args.get('width', '200')
    height = parsed_args.get('height', '200')
    zoom = parsed_args.get('zoom', 16)

    if not width.endswith('%') and not width.endswith('px'):
        width = width + 'px'
    if not height.endswith('%') and not height.endswith('px'):
        height = height + 'px'

    return dict(editable=editable, width=width, height=height, zoom=zoom,
            geojson=geojson, STATIC_URL=settings.STATIC_URL)
