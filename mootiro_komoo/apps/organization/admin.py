from django.contrib import admin
from reversion import VersionAdmin
from organization.models import Organization


class OrganizationAdmin(VersionAdmin):
    pass

admin.site.register(Organization, OrganizationAdmin)
