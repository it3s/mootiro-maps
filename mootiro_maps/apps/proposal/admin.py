from django.contrib import admin
from proposal.models import Proposal


class ProposalAdmin(admin.ModelAdmin):
    pass

admin.site.register(Proposal, ProposalAdmin)
