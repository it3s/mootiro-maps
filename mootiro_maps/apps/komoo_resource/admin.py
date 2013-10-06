from django.contrib import admin
from komoo_resource.models import Resource


class ResourceAdmin(admin.ModelAdmin):
    pass

admin.site.register(Resource, ResourceAdmin)
