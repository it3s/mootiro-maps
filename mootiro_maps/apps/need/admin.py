from django.contrib import admin
from need.models import NeedCategory, Need


class NeedAdmin(admin.ModelAdmin):
    pass

admin.site.register(Need, NeedAdmin)


class NeedCategoryAdmin(admin.ModelAdmin):
    pass

admin.site.register(NeedCategory, NeedCategoryAdmin)
