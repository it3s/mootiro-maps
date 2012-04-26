from django.contrib import admin
from reversion import VersionAdmin
from moderation.admin import abuse_reports
from community.models import Community


class CommunityAdmin(VersionAdmin):
    list_display = ('__unicode__', abuse_reports)

admin.site.register(Community, CommunityAdmin)
