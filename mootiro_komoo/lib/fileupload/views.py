from fileupload.models import UploadedFile
from django.views.generic import CreateView, DeleteView

from django.http import HttpResponse
from django.utils import simplejson
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, RequestContext
from django import forms


def response_mimetype(request):
    if "application/json" in request.META['HTTP_ACCEPT']:
        return "application/json"
    else:
        return "text/plain"


class FileCreateView(CreateView):
    model = UploadedFile

    def form_valid(self, form):
        self.object = form.save()
        f = self.request.FILES.get('file')
        data = [{'name': f.name,
                 'url': self.object.file.url,
                 'thumbnail_url': self.object.file.url,
                 'delete_url': reverse('upload-delete', args=[self.object.id]),
                 'delete_type': "DELETE",
                 'id': self.object.id}]
        response = JSONResponse(data, {}, response_mimetype(self.request))
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response

    # PLUPLOAD
    # def form_valid(self, form):
    #     self.object = form.save()
    #     # f = self.request.FILES.get('file')
    #     data = {'name': self.object.file.name.split('/')[-1],
    #              'url': self.object.file.url,
    #              'thumbnail_url': self.object.file.url,
    #              'delete_url': reverse('upload-delete', args=[self.object.id]),
    #              'delete_type': "DELETE",
    #              'id': self.object.id}
    #     response = JSONResponse(data, {}, response_mimetype(self.request))
    #     response['Content-Disposition'] = 'inline; filename=files.json'
    #     return response


class FileDeleteView(DeleteView):
    model = UploadedFile

    def delete(self, request, *args, **kwargs):
        """
        This does not actually delete the file, only the database record.  But
        that is easy to implement.
        """
        self.object = self.get_object()
        _id = self.object.id
        self.object.delete()
        response = JSONResponse({'deleted': True, 'id': _id}, {}, response_mimetype(self.request))
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response


class JSONResponse(HttpResponse):
    """JSON response class."""
    def __init__(self, obj='', json_opts={}, mimetype="application/json",
                 *args, **kwargs):
        content = simplejson.dumps(obj, **json_opts)
        super(JSONResponse, self).__init__(content, mimetype, *args, **kwargs)


from forms import PluploadWidget


class DummyForm(forms.Form):
    name = forms.CharField()
    desc = forms.CharField(widget=forms.Textarea())
    files_list = forms.CharField(widget=PluploadWidget())


def upload_poc(request):
    form = DummyForm()
    return render_to_response('plupload_poc.html', {'form': form},
                               context_instance=RequestContext(request))


def upload_poc_form(request):
    print 'POST: ', request.POST, '\n\n'
    return JSONResponse()
