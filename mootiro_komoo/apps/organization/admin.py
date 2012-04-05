from django.contrib import admin
from reversion import VersionAdmin
from organization.models import Organization, OrganizationBranch

class OrganizationBranchAdmin(VersionAdmin):
    pass

class OrganizationAdmin(VersionAdmin):
    pass

admin.site.register(OrganizationBranch, OrganizationBranchAdmin)
admin.site.register(Organization, OrganizationAdmin)
