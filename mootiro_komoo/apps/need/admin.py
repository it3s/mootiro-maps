from django.contrib import admin
from need.models import NeedCategory, Need
from reversion import VersionAdmin


class NeedAdmin(VersionAdmin):
    pass

admin.site.register(Need, NeedAdmin)


class NeedCategoryAdmin(VersionAdmin):
    pass

admin.site.register(NeedCategory, NeedCategoryAdmin)
