from ajax_select import LookupChannel
from django.utils.html import escape
from django.db.models import Q
from community.models import Community


class CommunityLookup(LookupChannel):

    model = Community

    def get_query(self, q, request):
        return Community.objects.filter(
            Q(name__icontains=q) | Q(slug__icontains=q))

    def get_result(self, obj):
        u"""
        simple text that is the completion of what the person typed
        """
        return obj.name

    def format_match(self, obj):
        """ (HTML) formatted item for display in the dropdown """
        return self.format_item_display(obj)

    def format_item_display(self, obj):
        """
        (HTML) formatted item for displaying item in the selected deck area
        """
        return u"<div>%s</div>" % (escape(obj.name))

    def check_auth(self, request):
        return True

    def can_add(self, user, argmodel):
        return True
