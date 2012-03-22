from django.contrib import admin
from reversion import VersionAdmin
from komoo_comments.models import Comment


class CommentAdmin(VersionAdmin):
    pass

admin.site.register(Comment, CommentAdmin)
