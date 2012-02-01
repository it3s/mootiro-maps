from django.http import HttpResponse

def new (request):
    return HttpResponse("Create new community.")
