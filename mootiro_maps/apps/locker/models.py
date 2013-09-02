# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models

from django.core.exceptions import ObjectDoesNotExist

from main.utils import randstr


class Locker(models.Model):
    '''Generic information storage class.'''

    key = models.CharField(max_length=32, null=False)
    data = models.TextField(null=False)
    expiration_date = models.DateTimeField(null=True)

    @classmethod
    def deposit(cls, data, expiration_date=None):
        '''
        Store data in a locker and return that locker's key. The locker remains
        until the expiration date or forever if no expiration date is provided.
        '''
        key = randstr(32)
        while Locker.objects.filter(key=key).exists():
            key = randstr(32)
        locker = Locker(key=key, data=data)
        if expiration_date:
            locker.expiration_date = expiration_date
        locker.save()
        return key

    @classmethod
    def withdraw(cls, key):
        '''
        Receives a locker's key, returns the data stored and destroys it.
        Returns None if no locker is matched.
        '''
        try:
            locker = Locker.objects.get(key=key)
        except ObjectDoesNotExist:
            return None
        data = locker.data
        locker.delete()
        return data
