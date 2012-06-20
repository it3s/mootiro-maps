# -*- coding: utf-8 -*-
import django.dispatch
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from signatures.models import Signature
from signatures.tasks import send_notification_mail
from organization.models import OrganizationBranch
from komoo_comments.models import Comment


send_notifications = django.dispatch.Signal(providing_args=["instance", ])


@receiver(send_notifications)
def notification_callback(sender, instance, *a, **kw):
    if isinstance(instance, OrganizationBranch):
        instance = instance.organization
    elif isinstance(instance, Comment):
        instance = instance.content_object
    content_type = ContentType.objects.get_for_model(instance)

    for signature in Signature.objects.filter(content_type=content_type,
        object_id=instance.id):
        send_notification_mail.delay(obj=instance, user=signature.user)


def notify_on_update(fn):
    """form save method decorator """
    def _notify_on_update(self, *a, **kw):
        r = fn(self, *a, **kw)
        if self.cleaned_data.get('id', None):
            send_notifications.send(sender=self, instance=r)
        elif hasattr(r, 'creator') and r.creator:
            # sign content on creation
            s = Signature(content_object=r, user=r.creator)
            s.save()
        return r
    return _notify_on_update
