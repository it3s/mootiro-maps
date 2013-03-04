# -*- coding: utf-8 -*-
from django import template
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from ..models import OrganizationBranch
from ajax_select.fields import AutoCompleteSelectMultipleWidget

register = template.Library()


@register.inclusion_tag('organization/branch_form.html', takes_context=True)
def branch_edit_form(context, id):
    branch = get_object_or_404(OrganizationBranch, pk=id)
    info_id = 'id_info_{}'.format(id)
    branch_community = AutoCompleteSelectMultipleWidget('community')
    branch_community = branch_community.render('branch_community',
        [c.id for c in branch.community.all()],
        attrs={'id': 'branch_community_{}'.format(id),
               'placeholder': _('Community')}
    )

    return dict(branch=branch, info_id=info_id, comm_widget=branch_community)
