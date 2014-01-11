from django.contrib import admin
from moderation.admin import abuse_reports
from community.models import Community


class CommunityAdmin(admin.ModelAdmin):
    #list_display = ('__unicode__', abuse_reports)
    pass

admin.site.register(Community, CommunityAdmin)
