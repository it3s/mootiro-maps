from django.contrib import admin
from django import forms

from moderation.admin import abuse_reports

from django import forms

from update.models import News


class NewsAdminForm(forms.ModelForm):
    class Meta:
        model = News

    description = forms.CharField(widget=forms.Textarea(), required=False)


class NewsAdmin(admin.ModelAdmin):
    form = NewsAdminForm

admin.site.register(News, NewsAdmin)
