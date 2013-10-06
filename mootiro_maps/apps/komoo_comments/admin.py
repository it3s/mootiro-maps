from django.contrib import admin
from komoo_comments.models import Comment


class CommentAdmin(admin.ModelAdmin):
    pass

admin.site.register(Comment, CommentAdmin)
