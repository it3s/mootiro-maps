from django import forms
from django.forms.widgets import flatatt
from django.utils.html import escape
from django.utils.simplejson import JSONEncoder


class JQueryAutoComplete(forms.TextInput):
    def __init__(self, source, options={}, attrs={}):
        """source can be a list containing the autocomplete values or a
        string containing the url used for the XHR request.

        For available options see the autocomplete sample page::
        http://jquery.bassistance.de/autocomplete/"""

        self.options = options
        self.attrs = {'autocomplete': 'off'}
        self.source = source

        self.attrs.update(attrs)

    def render_js(self, field_id):
        if isinstance(self.source, list):
            source = JSONEncoder().encode(self.source)
        elif isinstance(self.source, basestring):
            source = "%s" % escape(self.source)
        else:
            print type(self.source)
            raise ValueError('source type is not valid')

        o = {'source': str(source)}
        o.update(self.options)

        return u'$(\'#%s\').autocomplete(%s);' % (field_id, o)

    def render(self, name, value=None, attrs=None):
        final_attrs = self.build_attrs(attrs, name=name)
        if value:
            final_attrs['value'] = escape(unicode(value))

        if not self.attrs.has_key('id'):
            final_attrs['id'] = 'id_%s' % name

        return u'''<input type="text" %(attrs)s/>
        <script type="text/javascript"><!--//
        %(js)s//--></script>
        ''' % {
            'attrs' : flatatt(final_attrs),
            'js' : self.render_js(final_attrs['id']),
        }
