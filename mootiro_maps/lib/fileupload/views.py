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

from .forms import POCForm


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
        data = {
            'name': self.object.file.name.split('/')[-1],
            'url': self.object.file.url,
            'delete_url': reverse('upload-delete', args=[self.object.id]),
            'id': self.object.id,
            'size': self.object.file.size
        }
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
        # self.object.delete()
        self.object.content_object = None
        self.object.save()
#        try:
#            os.remove(path)
#        except Exception as err:
#            logger.warning('Failed to remove file: %s' % err)
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
        success = True
        file_ = {
            'name': uploaded_file.file.name.split('/')[-1],
            'url': uploaded_file.file.url,
            'delete_url': reverse('upload-delete', args=[uploaded_file.id]),
            'id': uploaded_file.id,
            'size': uploaded_file.file.size
        }
    else:
        success, file_ = False, {}

    response = JSONResponse({'success': success, 'file': file_}, {},
                                response_mimetype(request))
    return response


def uploader_poc(request):
    form = POCForm(request.POST or None)
    if form.is_valid():
        pass
    return render_to_response(
        'fileupload/poc.html',
        {'form_poc': form},
        context_instance=RequestContext(request))


def file_info(request):
    file_obj = UploadedFile.objects.get(pk=request.GET['id'])
    return JSONResponse(
        {
            'subtitle': file_obj.subtitle,
            'url': file_obj.file.url,
            'cover': file_obj.cover
        },
        {},
        response_mimetype(request))


def save_subtitle(request):
    try:
        file_obj = UploadedFile.objects.get(pk=request.POST['id'])
        file_obj.subtitle = request.POST.get('subtitle', '')
        file_obj.cover = (request.POST.get('cover', 'false') == 'true')
        file_obj.save()
        success = True
    except Exception:
        success = False
    return JSONResponse(
        {'success': success},
        {},
        response_mimetype(request))
