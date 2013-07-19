# -*- coding: utf-8 -*-
import simplejson

from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentTypeManager

from main.tests import KomooTestCase
from main.tests import logged_and_unlogged
from .models import Comment

from organization.models import Organization


def A_COMMENT_DATA():
    return {
        'comment': "This is awesome!!!!!!11",
        'content_type_id': 20,
        'object_id': 1,
    }.copy()
