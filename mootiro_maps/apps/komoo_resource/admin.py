from django.contrib import admin
from reversion import VersionAdmin
from komoo_resource.models import Resource


class ResourceAdmin(VersionAdmin):
    pass

admin.site.register(Resource, ResourceAdmin)
