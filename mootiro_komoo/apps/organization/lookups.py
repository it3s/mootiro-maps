from ajax_select import LookupChannel
from django.utils.html import escape
from django.db.models import Q
from organization.models import OrganizationCategory


class OrganizationCategoryLookup(LookupChannel):

    model = OrganizationCategory

    def get_query(self, q, request):
        return OrganizationCategory.objects.filter(
            Q(name__icontains=q) | Q(slug__icontains=q))
        # org_trans = OrganizationCategoryTranslation.objects.filter(
        #     Q(lang=settings.LANGUAGE_CODE) & (
        #     Q(name__icontains=q) | Q(slug__icontains=q)))

        # orgs = []
        # for o in org_trans:
        #     orgs.append(o.category)
        # return orgs

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

    # def can_add(self, user, argmodel):
    #     return True
