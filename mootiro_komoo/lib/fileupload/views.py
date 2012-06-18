import os
import logging
import urllib2
from fileupload.models import UploadedFile
from django.views.generic import CreateView, DeleteView
from django.conf import settings
from django.http import HttpResponse
from django.utils import simplejson
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, RequestContext
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile


logger = logging.getLogger(__name__)


def response_mimetype(request):
    if "application/json" in request.META['HTTP_ACCEPT']:
        return "application/json"
    else:
        return "text/plain"


class FileCreateView(CreateView):
    model = UploadedFile

    # PLUPLOAD
    def form_valid(self, form):
        self.object = form.save()
        # f = self.request.FILES.get('file')
        data = {'name': self.object.file.name.split('/')[-1],
                 'url': self.object.file.url,
                 'thumbnail_url': self.object.file.url,
                 'delete_url': reverse('upload-delete', args=[self.object.id]),
                 'delete_type': "DELETE",
                 'id': self.object.id}
        response = JSONResponse(data, {}, response_mimetype(self.request))
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response


class FileDeleteView(DeleteView):
    model = UploadedFile

    def delete(self, request, *args, **kwargs):
        """
        This does not actually delete the file, only the database record.  But
        that is easy to implement.
        """
        self.object = self.get_object()
        path = os.path.join(os.path.join(settings.PROJECT_ROOT,
                                     self.object.file.url[1:]))
        _id = self.object.id
        if hasattr(self.object.content_object, 'logo') and \
                self.object.content_object.logo == self.object:
            self.object.content_object.logo = None
            self.object.content_object.save()
        self.object.delete()
        try:
            os.remove(path)
        except Exception as err:
            logger.warning('Failed to remove file: %s' % err)
        response = JSONResponse({'deleted': True, 'id': _id}, {},
                                response_mimetype(self.request))
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response


class JSONResponse(HttpResponse):
    """JSON response class."""
    def __init__(self, obj='', json_opts={}, mimetype="application/json",
                 *args, **kwargs):
        content = simplejson.dumps(obj, **json_opts)
        super(JSONResponse, self).__init__(content, mimetype, *args, **kwargs)


def save_file_from_link(request):

    uploaded_file = UploadedFile()
    link = request.POST.get('file_link', None)
    if link:
        img_temp = NamedTemporaryFile(delete=True)
        img_temp.write(urllib2.urlopen(link).read())
        img_temp.flush()
        file_name = link.split('/')[-1]
        uploaded_file.file.save(file_name, File(img_temp))
        uploaded_file.save()
        success, _id = True, uploaded_file.id
    else:
        success, _id = False, ''

    response = JSONResponse({'success': success, 'id': _id}, {},
                                response_mimetype(request))
    return response


def uploader_poc(request):
    return render_to_response(
        'fileupload/poc.html',
        {},
        context_instance=RequestContext(request))
