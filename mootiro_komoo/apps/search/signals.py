# -*- coding: utf-8 -*-
import django.dispatch
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from signatures.models import Signature, DigestSignature, Digest
from signatures.tasks import send_notification_mail
from organization.models import OrganizationBranch
from komoo_comments.models import Comment


index_object_for_search = django.dispatch.Signal(providing_args=["obj", ])


@receiver(index_object_for_search)
def index_object_callback(sender, obj, *a, **kw):
    pass

