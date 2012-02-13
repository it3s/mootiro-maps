from django.contrib import admin
from need.models import NeedCategory

class NeedCategoryAdmin(admin.ModelAdmin):
    pass

admin.site.register(NeedCategory, NeedCategoryAdmin)
