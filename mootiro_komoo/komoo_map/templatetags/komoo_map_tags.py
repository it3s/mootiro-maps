#coding: utf-8
from django import template
from django.template.loader import render_to_string
from komoo_map.models import Address
register = template.Library()

@register.tag
def komoo_map(parser, token):
    """
    The syntax:
        {% komoo_map <address> [<width> <height>] [<zoom>] [<geojson>] [using <template_name>] %}
    """
    params = token.split_contents()

    if len(params) < 2:
        raise template.TemplateSyntaxError('komoo_map tag requires address argument')

    if len(params) == 3 or len(params) > 8:
        raise template.TemplateSyntaxError('komoo_map tag has the following syntax: '
                   '{% komoo_map <address> <width> <height> [zoom] [using <template_name>] %}')
    return KomooMapNode(params)

@register.tag
def komoo_map_editor(parser, token):
    """
    The syntax:
        {% komoo_map_editor <address> [<width> <height>] [<zoom>] [<geojson>] [using <template_name>] %}
    """
    params = token.split_contents()

    if not params[-2] == 'using':
        params = params + ['using', '"komoo_map/editor.html"']

    if len(params) < 2:
        raise template.TemplateSyntaxError('komoo_map_editor tag requires address argument')

    if len(params) == 3 or len(params) > 8:
        raise template.TemplateSyntaxError('komoo_map_editor tag has the following syntax: '
                   '{% komoo_map_editor <address> <width> <height> [zoom] [using <template_name>] %}')
    return KomooMapNode(params)

class KomooMapNode(template.Node):
    def __init__(self, params):
        width, height, zoom, geojson, template_name = None, None, None, None, None
        # pop the template name
        if params[-2] == 'using':
            template_name = params[-1]
            params = params[:-2]

        address = params[1]

        if len(params) == 4:
            width, height = params[2], params[3]
        elif len(params) == 5:
            width, height, zoom = params[2], params[3], params[4]
        elif len(params) == 6:
            width, height, zoom, geojson = params[2], params[3], params[4], params[5]

        self.address = template.Variable(address)
        self.width = template.Variable(width or '')
        self.height = template.Variable(height or '')
        self.zoom = template.Variable(zoom or 16)
        self.geojson = template.Variable(geojson or '{}')
        self.template_name = template.Variable(template_name or '"komoo_map/map.html"')

    def render(self, context):
        try:
            address = self.address.resolve(context)
            template_name = self.template_name.resolve(context)
            width = self.width.resolve(context)
            height = self.height.resolve(context)
            zoom = self.zoom.resolve(context)
            geojson = self.geojson.resolve(context)

            map_, _ = Address.objects.get_or_create(address=address or '')
            if not map_.latitude:
                map_.latitude = -23.55
                map_.longitude = -46.65
            context.update({
                'map': map_,
                'width': width,
                'height': height,
                'zoom': zoom,
                'geojson': geojson,
                'template_name': template_name
            })
            return render_to_string(template_name, context_instance=context)
        except template.VariableDoesNotExist:
            return ''
