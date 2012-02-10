from django.forms import Textarea
from django.template import Template, Context


#TODO: Update the form field when change the map overlays.
class AddressWithMapWidget(Textarea):
    def render(self, name, value, attrs=None):
        default_html = super(AddressWithMapWidget, self).render(name, value, attrs)
        map_template = Template("{% load komoo_map_tags %}{% komoo_map_editor address width height zoom geojson %}")
        #TODO: Make parameters configurable
        context = Context({
            'address': '',
            'width': 700,
            'height': 600,
            'zoom': 13,
            'geojson': value or '{}'
        })
        return default_html + map_template.render(context)
