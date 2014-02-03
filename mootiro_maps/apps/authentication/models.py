# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from hashlib import sha1
import os

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import translation
from django.core.urlresolvers import reverse
from jsonfield import JSONField

from main.mixins import BaseModel
from main.utils import build_obj_from_dict
from locker.models import Locker
from main.tasks import send_mail_async
from main.models import ContactsField
from komoo_map.models import GeoRefModel, POINT
from search.signals import index_object_for_search
from fileupload.models import UploadedFile


CONFIRMATION_EMAIL_MSG = _('''
Hello, {name}.

Before using our tool, please confirm your email visiting the link below.
{verification_url}

Thanks,
the IT3S team
''')


class User(GeoRefModel, BaseModel):
    """
    User model. Replaces django.contrib.auth, CAS and social_auth
    with our own unified solution.
    its intended to use with external login providers.

    password: is set only if not created through external providers

    """
    name = models.CharField(max_length=256, null=False)
    email = models.CharField(max_length=512, null=False, unique=True)
    about_me = models.TextField(null=True, blank=True, default='')
    password = models.CharField(max_length=256, null=False)
    contacts = ContactsField()
    creation_date = models.DateField(null=True, blank=True, auto_now_add=True)
    language = models.CharField(max_length=10, null=True, blank=True)
    # last_access = models.DateTimeField(null=True, blank=True)

    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    # Deprecated
    # verification_key = models.CharField(max_length=32, null=True)

    # Attributes used by PermissionMixin
    private_fields = ['email']
    internal_fields = ['password']

    class Map:
        editable = False
        geometries = [POINT]
        categories = ['me', 'user']
        min_zoom_geometry = 0
        max_zoom_geometry = 100
        min_zoom_point = 100
        max_zoom_point = 100
        min_zoom_icon = 100
        max_zoom_icon = 10

    @classmethod
    def calc_hash(self, s, salt=None):
        if not salt:
            salt = settings.USER_PASSWORD_SALT
        return unicode(sha1(salt + s).hexdigest())

    def set_password(self, s, salt=None):
        self.password = self.calc_hash(s, salt=salt)

    def set_language(self, language_code):
        if translation.check_for_language(language_code):
            self.language = language_code
            return True
        return False

    def verify_password(self, s, salt=None):
        return self.password == self.calc_hash(s, salt)

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def is_superuser(self):
        return self.is_admin

    def __unicode__(self):
        return unicode(self.name)

    @property
    def url(self):
        return reverse('user_view', kwargs={'id': self.id})

    @property
    def view_url(self):
        return self.url

    def files_set(self):
        """ pseudo-reverse query for retrieving Resource Files"""
        return UploadedFile.get_files_for(self)

    @property
    def avatar(self):
        url = '{}img/user-placeholder.png'.format(settings.STATIC_URL)
        files = self.files_set()
        for fl in files:
            if os.path.exists(fl.file.url[1:]):
                url = fl.file.url
                break
        return url

    def _social_auth_by_name(self, name):
        """
        Retrieve the SocialAuth entry for this User given a high level
        social provider name.
        """
        credentials = self.socialauth_set.filter(provider=PROVIDERS[name])
        return credentials.get() if credentials.exists() else None

    def google(self):
        return self._social_auth_by_name('google')

    def facebook(self):
        return self._social_auth_by_name('facebook')

    # ==================== Interface for django admin ======================= #
    def is_staff(self):
        return self.is_admin

    def has_module_perms(self, mod):
        return self.is_admin

    def has_perm(self, perm):
        return self.is_admin

    # dummy fix for django weirdness =/
    def get_and_delete_messages(self):
        pass

    # ====================  utils =========================================== #
    def from_dict(self, data):
        keys = [
            'id', 'name', 'email', 'password', 'contacts', 'geojson',
            'creation_date', 'is_admin', 'is_active', 'about_me']
        date_keys = ['creation_date']
        build_obj_from_dict(self, data, keys, date_keys)

    def to_dict(self):
        fields_and_defaults = [
            ('id', None), ('name', None), ('email', None), ('contacts', {}),
            ('geojson', {}), ('url', ''), ('password', None),
            ('creation_date', None), ('is_admin', False), ('is_active', False),
            ('avatar', None), ('about_me', '')
        ]
        dict_ = {v[0]: getattr(self, v[0], v[1])
                    for v in fields_and_defaults}
        return dict_

    def is_valid(self, ignore=[]):
        self.errors = {}
        valid = True

        # verify required fields
        required = ['name', 'email', 'password']
        for field in required:
            if not field in ignore and not getattr(self, field, None):
                valid, self.errors[field] = False, _('Required field')

        if not self.id:
            # new User
            if SocialAuth.objects.filter(email=self.email).exists():
                valid = False
                self.errors['email'] = _('This email is registered on our '
                    'system. You might have logged before with a social '
                    'account (Facebook or Google). Please, skip this step '
                    'and just login.')

            if User.objects.filter(email=self.email).exists():
                valid = False
                self.errors['email'] = _('Email address already in use')

        return valid

    def send_confirmation_mail(self, request):
        """ send async confirmation mail """
        key = Locker.deposit(self.id)
        verification_url = request.build_absolute_uri(
                reverse('user_verification', args=(key,)))
        send_mail_async(
            title=_('Welcome to MootiroMaps'),
            receivers=[self.email],
            message=CONFIRMATION_EMAIL_MSG.format(
                name=self.name,
                verification_url=verification_url))

    # DEPRECATED
    # def contributions(self, page=1, num=None):
    #     """ return user's update """
    #     return get_user_updates(self, page=page, num=num)

    #### Compatibility (to be deprecated soon)
    def get_first_name(self):
        return self.name.split(' ')[0]

    def save(self, *args, **kwargs):
        r = super(User, self).save(*args, **kwargs)
        index_object_for_search.send(sender=self, obj=self)
        return r

    def projects_contributed(self):
        from komoo_project.models import Project
        return Project.get_projects_for_contributor(self)


class AnonymousUser(object):
    '''Dummy Class to integrate with other django apps.'''
    def is_authenticated(self):
        return False

    def is_anonymous(self):
        return True

    def is_superuser(self):
        return self.is_admin

    def is_admin(self):
        return False

    def is_active(self):
        return False

    def is_staff(self):
        return False

    def has_perm(self, *args):
        return False

    name = ''
    id = None

    def to_dict(self):
        return {'id': None}

    def to_cleaned_dict(self, *args, **kwargs):
        return self.to_dict()

    # dummy fix for django weirdness =/
    def get_and_delete_messages(self):
        pass


PROVIDERS = {
    # 'provider label': 'db info'
    'facebook': 'facebook-oauth2',
    'google': 'google-oauth2',
    # 'twitter': 'twitter-oauth2',
}
PROVIDERS_CHOICES = [(t[1], t[0]) for t in PROVIDERS.items()]


class SocialAuth(models.Model):
    """
    User credentials for login on external authentication providers as Google,
    Facebook and Twitter.
    """

    user = models.ForeignKey(User)
    provider = models.CharField(max_length=32, choices=PROVIDERS_CHOICES)
    email = models.CharField(max_length=256)
    data = JSONField()  # provider specific data for user login
