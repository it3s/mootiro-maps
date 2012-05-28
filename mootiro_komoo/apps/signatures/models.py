# -*- coding: utf-8 -*-
from django.db import models
from django.core.mail import EmailMultiAlternatives
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic


class Signature(models.Models):
    user = models.ForeignKey(User)
    content_type = models.ForeignKey(ContentType,  null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    digest = models.BooleanField(default=False)


class MailMessage(models.Model):
    subject = models.CharField(max_length=250, blank=True, null=True)
    to_address = models.EmailField(max_length=250)
    from_address = models.EmailField(max_length=250)
    content = models.TextField(blank=True, null=True)
    sent = models.BooleanField(default=False, editable=False)

    def __unicode__(self):
        return self.subject

    def send(self):
        if not self.sent:
            try:
                msg = EmailMultiAlternatives(self.subject, self.content,
                        self.from_address, [self.to_address])
                msg.send()
                self.sent = True
                self.save()
            except:
                pass


@receiver(post_save, sender=MailMessage)
def send_post_save(sender, instance, signal, *args, **kwargs):
    # TODO implement-me: send to celery task queue
    pass
