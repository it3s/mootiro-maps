from django.forms import HiddenInput
from django.template import Template, Context


#TODO: Update the form field when change the map overlays.
class AddressWithMapWidget(HiddenInput):
    def render(self, name, value, attrs=None):
        print attrs
        default_html = super(AddressWithMapWidget, self).render(name, value, attrs)
        map_template = Template('{% load komoo_map_tags %}{% komoo_map_editor address width height zoom geojson id %}')
        #TODO: Make parameters configurable
        context = Context({
            'address': '',
            'width': '100%',
            'height': '600',
            'zoom': 13,
            'geojson': value or '{}',
            'id': attrs.get('id')
        })
        return default_html + map_template.render(context)
