#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django.forms import ModelForm, Form, CharField
from komoo_map.widgets import AddressWithMapWidget
from community.models import Community

from main.fields import TagsField
from main.widgets import Tagsinput


class CommunityForm(ModelForm):
    class Meta:
        model = Community
    
	tags = TagsField(widget=Tagsinput(autocomplete_url="/need/tag_search"))


class CommunityMapForm(Form):
    map = CharField(widget=AddressWithMapWidget, required=False)
