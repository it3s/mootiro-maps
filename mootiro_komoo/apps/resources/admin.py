from django.contrib import admin
from reversion import VersionAdmin
from resources.models import Resource


class ResourceAdmin(VersionAdmin):
    pass

admin.site.register(Resource, ResourceAdmin)
