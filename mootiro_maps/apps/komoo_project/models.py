# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import itertools

from django.db import models
from django.db.models import Q
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.gis.db import models as geomodels
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify

from lib.taggit.managers import TaggableManager
from fileupload.models import UploadedFile
from jsonfield import JSONField

from authentication.models import User
from community.models import Community
from search.signals import index_object_for_search
from main.utils import create_geojson, to_json
from main.models import ContactsField
from main.mixins import BaseModel
from komoo_map.models import get_models


class ProjectRelatedObject(models.Model):
    project = models.ForeignKey('Project')

    # dynamic ref
    content_type = models.ForeignKey(ContentType, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')


class Layer(models.Model):
    project = models.ForeignKey('Project', related_name='project_layers')

    name = models.CharField(max_length=1024)
    position = models.PositiveSmallIntegerField(null=True)
    visible = models.NullBooleanField()
    rule = JSONField();
    fillColor = models.CharField(max_length=10)
    strokeColor = models.CharField(max_length=10)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'fillColor': self.fillColor,
            'strokeColor': self.strokeColor,
            'rule': self.rule,
            'position': self.position
        }

    @property
    def json(self):
        return to_json(self.to_dict())


    def from_dict(self, data):
        self.name = data.get('name')
        self.position = data.get('position')
        self.rule = data.get('rule', {})
        self.fillColor = data.get('fillColor');
        self.strokeColor = data.get('strokeColor');


class Project(BaseModel, geomodels.Model):
    name = models.CharField(max_length=1024)
    slug = models.SlugField(max_length=1024)
    description = models.TextField()
    short_description = models.CharField(max_length=250, null=True, blank=True)

    tags = TaggableManager()

    contributors = models.ManyToManyField(User, null=True, blank=True,
            related_name='project_contributors')
    community = models.ManyToManyField(Community, null=True, blank=True)

    contacts = ContactsField()

    logo = models.ForeignKey(UploadedFile, null=True, blank=True)

    creator = models.ForeignKey(User, editable=False, null=True,
            related_name='created_projects')
    creation_date = models.DateTimeField(auto_now_add=True)
    last_editor = models.ForeignKey(User, editable=False, null=True,
            blank=True, related_name='project_last_editor')
    last_update = models.DateTimeField(auto_now=True)

    maptype = models.CharField(max_length=32, default='clean', editable=False)
    bounds_cache = geomodels.PolygonField(null=True, blank=True, editable=False)
    custom_bounds = geomodels.PolygonField(null=True, blank=True, editable=False)

    def __unicode__(self):
        return unicode(self.name)

    def slug_exists(self, slug):
        return Project.objects.filter(slug=slug).exists()

    def save(self, *a, **kw):
        self.slug = slugify(self.name)
        r = super(Project, self).save(*a, **kw)
        index_object_for_search.send(sender=self, obj=self)
        return r

    def partners_logo(self):
        """ pseudo-reverse query for retrieving the partners logo"""
        return UploadedFile.get_files_for(self)

    @property
    def all_contributors(self):
        seen = set()
        seen_add = seen.add
        iterable = itertools.chain(self.contributors.all(), [self.creator])
        for element in itertools.ifilterfalse(seen.__contains__, iterable):
            seen_add(element)
            yield element

    @property
    def layers(self):
        return [layer.to_dict() for layer in self.project_layers.order_by('position')]

    @layers.setter
    def layers(self, data):
        for layer_ in data:
            id = layer_.get('id', None)
            if not id:  # Create new layer
                layer = Layer()
                layer.project = self
            else:
                layer = Layer.objects.get(id=int(id))

            if layer_.get('delete', False):
                # The layers is marked to be removed
                layer.delete()
            else:
                layer.from_dict(layer_)
                layer.save()

    @property
    def public(self):
        ''' Temporary property to avoid crashes. '''
        return True

    @property
    def public_discussion(self):
        ''' Temporary property to avoid crashes. '''
        return True

    def user_can_edit(self, user):
        return True

    def user_can_discuss(self, user):
        return True

    @property
    def home_url_params(self):
        return dict(id=self.id)

    @property
    def view_url(self):
        return reverse('project_view', kwargs=self.home_url_params)

    @property
    def edit_url(self):
        return reverse('project_edit', kwargs=self.home_url_params)

    @property
    def perm_id(self):
        return 'j%d' % self.id  # project, and not Proposal

    @property
    def logo_url(self):
        if self.logo:
            return self.logo.file.url
        else:
            return '{}img/project-placeholder.png'.format(settings.STATIC_URL)

    @property
    def related_objects(self):
        """Returns a queryset for the objects for a given project"""
        return ProjectRelatedObject.objects.filter(project=self)

    def filter_related_items(self, query, models):
        items = []
        for model in models:
            ct = ContentType.objects.get_for_model(model)
            obj_ids = (self.related_objects.values_list("object_id", flat=True)
                       .filter(content_type=ct))
            obj = model.objects.filter(Q(pk__in=obj_ids) & query)
            for o in obj:
                items.append(o)
        return items

    def save_related_object(self, related_object, user=None, silent=False):
        ct = ContentType.objects.get_for_model(related_object)
        # Adds the object to project
        obj, created = ProjectRelatedObject.objects.get_or_create(
                content_type_id=ct.id, object_id=related_object.id,
                project_id=self.id)
        self._update_bounds_cache()
        if user:
            # Adds user as contributor
            self.contributors.add(user)
            # Creates update entry
            if created and not silent:
                from update.models import Update
                from update.signals import create_update
                create_update.send(sender=obj.__class__, user=user,
                                    instance=obj, type=Update.EDIT)
        return created

    @property
    def related_items(self):
        #return itertools.chain(self.all_contributors,
        #                       self.filter_related_items(Q(), get_models()))
        return self.filter_related_items(Q(), get_models())

    @property
    def bounds(self):
        if not self.bounds_cache:
            self._update_bounds_cache()
        return self.bounds_cache

    def _update_bounds_cache(self):
        # Get the project items
        items = self.related_items
        bounds = None
        for item in items:
            if not item.geometry.empty:
                if not bounds:
                    bounds = item.bounds
                else:
                    bounds = bounds.union(item.bounds).envelope
        self.bounds_cache = bounds
        self.save()
        return bounds

    @property
    def bbox(self):
        coords = self.bounds.coords[0]
        return [coords[0][1], coords[0][0], coords[2][1], coords[2][0]]


    @property
    def json(self):
        return to_json({
            'name': self.name,
            'slug': self.slug,
            'logo_url': self.logo_url,
            'view_url': self.view_url,
            'partners_logo': [{'url': logo.file.url}
                                for logo in self.partners_logo()],
            'bounds': self.bounds,
        })

    @property
    def geojson(self):
        items = []
        for obj in self.related_items:
            if obj and not obj.is_empty():
                items.append(obj)
        return create_geojson(items)

    @classmethod
    def get_projects_for_contributor(cls, user):
        return Project.objects.filter(
            Q(contributors__in=[user]) | Q(creator=user)).distinct()

    # ==========================================================================
    # Utils

    # def from_dict(self, data):
    #     keys = ['id', 'name', 'contact', 'geojson',  'creation_date',
    #             'is_admin', 'is_active', 'about_me']
    #     date_keys = ['creation_date']
    #     build_obj_from_dict(self, data, keys, date_keys)

    def to_dict(self):
        fields_and_defaults = [
            ('name', None), ('slug', None), ('description', None),
            ('short_description ', None),
            ('creator_id', None), ('creation_date', None),
            ('last_editor_id', None), ('last_update', None),
            ('logo_id', None),
            ('contacts', {}),
            ('bounds', None),
        ]
        dict_ = {v[0]: getattr(self, v[0], v[1]) for v in fields_and_defaults}
        dict_['tags'] = [tag.name for tag in self.tags.all()]
        dict_['community'] = [comm.id for comm in self.community.all()]
        dict_['contributors'] = [cont.name for cont in self.contributors.all()]
        # TODO: related_objects
        return dict_

    # def is_valid(self, ignore=[]):
    #     self.errors = {}
    #     valid = True
    #     return valid

