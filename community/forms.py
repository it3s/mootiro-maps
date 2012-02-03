#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django.forms import ModelForm
from mootiro_komoo.community.models import Community


class CommunityForm(ModelForm):
    class Meta:
        model = Community
