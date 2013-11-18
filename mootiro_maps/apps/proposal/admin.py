from django.contrib import admin
from reversion import VersionAdmin
from proposal.models import Proposal


class ProposalAdmin(VersionAdmin):
    pass

admin.site.register(Proposal, ProposalAdmin)
