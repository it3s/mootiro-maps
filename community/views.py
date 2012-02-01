from django.shortcuts import render_to_response
from django.template import RequestContext

from mootiro_komoo.community.models import Community
from mootiro_komoo.community.forms import CommunityForm

def new (request):
    community_form = CommunityForm()
    context = {
        'form': community_form
    }
    return render_to_response('new.html', context,
            context_instance=RequestContext(request))

def save (request):
    community = CommunityForm(request.POST)
    community.save()
    return render_to_response('new.html')

def map (request, slug):
    community = Community.objects.get(slug=slug)
    return render_to_response('map.html', {'community': community},
            context_instance=RequestContext(request))
