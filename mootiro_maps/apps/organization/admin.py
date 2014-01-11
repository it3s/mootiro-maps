from django.contrib import admin
from organization.models import Organization


class OrganizationAdmin(admin.ModelAdmin):
    pass

admin.site.register(Organization, OrganizationAdmin)
