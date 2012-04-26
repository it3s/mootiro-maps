from django.contrib import admin
from django.contrib.contenttypes import generic
from moderation.models import Moderation


def abuse_reports(obj):
    reports = Moderation.objects.get_for_object(obj).count()
    return reports
abuse_reports.allow_tags = True


def delete_object(modeladmin, request, queryset):
    for obj in queryset:
        if modeladmin.has_delete_permission(request, obj):
            obj.content_object.delete()
            obj.delete()
delete_object.short_description = "Delete the reported object"


class ModerationInline(generic.GenericTabularInline):
    model = Moderation


class ModerationAdmin(admin.ModelAdmin):
    list_display = ('content_object', 'reason', 'user', 'date')
    list_filter = ('object_id', 'reason', )
    actions = (delete_object, )


admin.site.register(Moderation, ModerationAdmin)
