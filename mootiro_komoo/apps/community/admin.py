from django.contrib import admin
from reversion import VersionAdmin
from community.models import Community


class CommunityAdmin(VersionAdmin):
    pass

admin.site.register(Community, CommunityAdmin)
