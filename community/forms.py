from django.forms import ModelForm

from mootiro_komoo.community.models import Community


class CommunityForm(ModelForm):
    class Meta:
        model = Community
