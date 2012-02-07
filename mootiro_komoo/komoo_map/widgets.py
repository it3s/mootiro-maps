from django.forms import TextInput
from django.template import Template, Context

class AddressWithMapWidget(TextInput):
    def render(self, name, value, attrs=None):
        default_html = super(AddressWithMapWidget, self).render(name, value, attrs)
        map_template = Template("{% load komoo_map_tags %}{% komoo_map address 700 200 16 %}")
        context = Context({'address': value})
        return default_html + map_template.render(context)
