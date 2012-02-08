from django import forms
from widgets import Tagsinput

class TagsField(forms.CharField):
    widget = Tagsinput

    def to_python(self, value):
        """Normalize comma separated string to a list of tags"""
        return value.split(',')
