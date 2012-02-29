# -*- coding:utf-8 -*-
from django import template
from django.contrib.contenttypes.models import ContentType

register = template.Library()


@register.inclusion_tag('vote/vote_templatetag.html', takes_context=True)
def vote(context, content_object):
    """
    Templatetags for Votes. It works for any given content_object.
    usage:
        {% vote any_object %}
    """
    c = ContentType.objects.get_for_model(content_object)
    votes = {'up': 0, 'down': 0}
    return dict(content_type=c.id, object_id=content_object.id, votes=votes)


@register.inclusion_tag('vote/vote_staticfiles.html')
def comments_staticfiles():
    """Static files (javascript/css) for the votes templatetag"""
    return {}
