#coding: utf-8
from django import template
from django.template.loader import render_to_string
from komoo_map.models import Address
register = template.Library()

@register.tag
def komoo_map(parser, token):
    """
    The syntax:
        {% komoo_map [<width> <height>] [<zoom>] [<geojson>] [using <template_name>] %}
    """
    params = token.split_contents()

    if len(params) > 7:
        raise template.TemplateSyntaxError('komoo_map tag has the following syntax: '
                   '{% komoo_map <width> <height> [zoom] [using <template_name>] %}')
    return KomooMapNode(params)

@register.tag
def komoo_map_editor(parser, token):
    """
    The syntax:
        {% komoo_map_editor [<width> <height>] [<zoom>] [<geojson>] [using <template_name>] %}
    """
    params = token.split_contents()

    if not params[-2] == 'using':
        params = params + ['using', '"komoo_map/editor.html"']

    if len(params) > 7:
        raise template.TemplateSyntaxError('komoo_map_editor tag has the following syntax: '
                   '{% komoo_map_editor <width> <height> [zoom] [<geojson>] [using <template_name>] %}')
    return KomooMapNode(params)

class KomooMapNode(template.Node):
    def __init__(self, params):
        width, height, zoom, geojson, template_name = None, None, None, None, None
        # pop the template name
        if params[-2] == 'using':
            template_name = params[-1]
            params = params[:-2]

        if len(params) == 3:
            width, height = params[1:3]
        elif len(params) == 4:
            width, height, zoom = params[1:4]
        elif len(params) == 5:
            width, height, zoom, geojson = params[1:5]

        self.width = template.Variable(width or '')
        self.height = template.Variable(height or '')
        self.zoom = template.Variable(zoom or 16)
        self.geojson = template.Variable(geojson or '{}')
        self.template_name = template.Variable(template_name or '"komoo_map/map.html"')

    def render(self, context):
        #try:
            template_name = self.template_name.resolve(context)
            width = self.width.resolve(context)
            height = self.height.resolve(context)
            zoom = self.zoom.resolve(context)
            geojson = self.geojson.resolve(context)

            if not width.endswith('%') and not width.endswith('px'):
                width = width + 'px'
            if not height.endswith('%') and not height.endswith('px'):
                height = height + 'px'

            context.update({
                'width': width,
                'height': height,
                'zoom': zoom,
                'geojson': geojson,
                'template_name': template_name
            })
            return render_to_string(template_name, context_instance=context)
        #except template.VariableDoesNotExist:
        #    return 'ERRO'
