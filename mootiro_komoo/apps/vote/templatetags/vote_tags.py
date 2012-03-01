# -*- coding:utf-8 -*-
from django import template
from django.contrib.contenttypes.models import ContentType
from ..models import Vote
register = template.Library()


@register.inclusion_tag('vote/vote_templatetag.html', takes_context=True)
def vote(context, content_object):
    """
    Templatetags for Votes. It works for any given content_object.
    usage:
        {% vote any_object %}
    """
    c = ContentType.objects.get_for_model(content_object)
    votes_queryset = Vote.get_votes_for(content_object)
    votes = {'up': votes_queryset.filter(like=True).count(),
             'down': votes_queryset.filter(like=False).count()}
    if 'user' in context and not context['user'].is_anonymous():
        user_vote_query = votes_queryset.filter(author=context['user'])
        if user_vote_query.count():
            user_vote = 'up' if user_vote_query[0].like else 'down'
        else:
            user_vote = None
    else:
        user_vote = None

    return dict(content_type=c.id, object_id=content_object.id, votes=votes,
                user_vote=user_vote)


@register.inclusion_tag('vote/vote_staticfiles.html', takes_context=True)
def vote_staticfiles(context):
    """Static files (javascript/css) for the votes templatetag"""
    return {}
