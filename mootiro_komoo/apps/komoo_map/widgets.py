from django.conf import settings
from django.forms import HiddenInput
from django.template import Template, Context


#TODO: Update the form field when change the map overlays.
class AddressWithMapWidget(HiddenInput):
    class Media:
        js = ('http://maps.google.com/maps/api/js?sensor=false&libraries=drawing',
              'http://www.google.com/jsapi',
              'js/infobox_packed.js',
              'js/markerclusterer_packed.js',
              'js/komoo_map.js')

    def render(self, name, value, attrs=None):
        default_html = super(AddressWithMapWidget, self).render(name, value, attrs)
        map_template = Template('{% load komoo_map_tags %}{% komoo_map geojson editor width height zoom %}')
        #TODO: Make parameters configurable
        context = Context({
            'editor': 'editable=True',
            'width': 'width=100%',
            'height': 'height=600',
            'zoom': 'zoom=13',
            'geojson': value or '{}',
            'STATIC_URL': settings.STATIC_URL
        })
        return default_html + map_template.render(context)
