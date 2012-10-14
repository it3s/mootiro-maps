# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import simplejson

from django.db import models
from django.contrib.contenttypes import generic
from django.template.defaultfilters import slugify
from django.conf import settings
from django.core.urlresolvers import reverse

from django.utils.translation import ugettext as _

from komoo_user.models import User
from komoo_map.models import GeoRefModel, POLYGON, POINT
from community.models import Community
from need.models import TargetAudience
from proposal.models import Proposal
from komoo_resource.models import Resource
from investment.models import Investment, Investor
from fileupload.models import UploadedFile
from lib.taggit.managers import TaggableManager


LOGO_CHOICES = (
    ('UP', 'Uploaded'),
    ('CAT', 'Category'),
)


class Organization(models.Model):
    name = models.CharField(max_length=320, unique=True)
    slug = models.SlugField(max_length=320, db_index=True)
    description = models.TextField(null=True, blank=True)
    logo = models.ForeignKey(UploadedFile, null=True, blank=True)
    logo_category = models.ForeignKey('OrganizationCategory', null=True,
                       blank=True, related_name='organization_category_logo')
    logo_choice = models.CharField(max_length=3, choices=LOGO_CHOICES,
                        null=True, blank=True)

    # Meta info
    creator = models.ForeignKey(User, editable=False, null=True,
                        related_name='created_organizations')
    creation_date = models.DateTimeField(auto_now_add=True)
    last_editor = models.ForeignKey(User, editable=False, null=True,
                        blank=True)
    last_update = models.DateTimeField(auto_now=True)

    community = models.ManyToManyField(Community, null=True, blank=True)

    link = models.CharField(max_length=250, null=True, blank=True)
    contact = models.TextField(null=True, blank=True)

    categories = models.ManyToManyField('OrganizationCategory', null=True,
                        blank=True)
    target_audiences = models.ManyToManyField(TargetAudience, null=True,
                        blank=True)

    tags = TaggableManager()

    investments = generic.GenericRelation(Investment,
                        content_type_field='grantee_content_type',
                        object_id_field='grantee_object_id')

    @property
    def related_items(self):
        return [c for c in self.community.all()] + \
            [b for b in self.organizationbranch_set.all()] + \
            [r for r in self.supported_resources] + \
            [p.need for p in self.supported_proposals] + \
            [b for o in self.supported_organizations
                    for b in o.organizationbranch_set.all()]

    @property
    def as_investor(self):
        investor, created = Investor.get_or_create_for(self)
        return investor

    @property
    def realized_investments(self):
        return self.as_investor.investments.all()

    @property
    def supported_organizations(self):
        return [i.grantee for i in self.realized_investments
                if isinstance(i.grantee, Organization)]

    @property
    def supported_proposals(self):
        return [i.grantee for i in self.realized_investments
                if isinstance(i.grantee, Proposal)]

    @property
    def supported_resources(self):
        return [i.grantee for i in self.realized_investments
                if isinstance(i.grantee, Resource)]

    def __unicode__(self):
        return unicode(self.name)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        return super(Organization, self).save(*args, **kwargs)

    def files_set(self):
        """ pseudo-reverse query for retrieving Organization Files"""
        return UploadedFile.get_files_for(self)

    @property
    def branch_count(self):
        count = OrganizationBranch.objects.filter(organization=self).count()
        return count

    @property
    def logo_url(self):
        if self.logo and not self.logo_category:
            return self.logo.file.url
        elif not self.logo and self.logo_category:
            return '/static/' + self.logo_category.image
        else:
            if self.logo_choice == 'CAT':
                return '/static/' + self.logo_category.image
            elif self.logo_choice == 'UP':
                return self.logo.file.url
            else:
                return '/static/img/logo.png'

    image = "img/organization.png"
    image_off = "img/organization-off.png"

    # url aliases
    @property
    def home_url_params(self):
        return dict(id=self.id)

    @property
    def view_url(self):
        return reverse('view_organization', kwargs=self.home_url_params)

    @property
    def edit_url(self):
        return reverse('edit_organization', kwargs=self.home_url_params)

    @property
    def admin_url(self):
        return reverse('admin:{}_{}_change'.format(self._meta.app_label,
            self._meta.module_name), args=[self.id])

    @property
    def new_investment_url(self):
        return reverse('new_investment') + ('?type=organization&obj=%(id)s' % {
                'id': self.id})

    @property
    def related_items_url(self):
        return reverse('view_organization_related_items',
                       kwargs=self.home_url_params)

    @property
    def json(self):
        return simplejson.dumps({
            'name': self.name,
            'slug': self.slug,
            'logo_url': self.logo_url,
            'view_url': self.view_url,
        })

    def perm_id(self):
        return 'o%d' % self.id


class OrganizationBranch(GeoRefModel, models.Model):
    name = models.CharField(max_length=320)
    slug = models.SlugField(max_length=320)

    organization = models.ForeignKey(Organization)
    info = models.TextField(null=True, blank=True)

    creation_date = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, null=True, blank=True)

    community = models.ManyToManyField(Community, null=True, blank=True)

    class Map:
        editable = True
        title = _('Organization')
        tooltip = _('Add Organization')
        background_color = '#3a61d6'
        border_color = '#1f49b2'
        geometries = (POLYGON, POINT)
        form_view_name = 'new_organization_from_map'

    def __unicode__(self):
        return unicode('{organization} - {branch}'.format(
                organization=self.organization.name, branch=self.name))

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        return super(OrganizationBranch, self).save(*args, **kwargs)

    @property
    def description(self):
        return self.info

    @property
    def view_url(self):
        return self.organization.view_url

    @property
    def edit_url(self):
        return self.organization.edit_url

    @property
    def related_items(self):
        return self.organization.related

    image = "img/organization.png"
    image_off = "img/organization-off.png"


class OrganizationCategory(models.Model):
    name = models.CharField(max_length=320, unique=True)
    slug = models.CharField(max_length=320, unique=True, blank=True)

    def __unicode__(self):
        return unicode(self.name)

    def save(self, *a, **kw):
        self.slug = slugify(self.name)
        return super(OrganizationCategory, self).save(*a, **kw)

    def get_translated_name(self):
        if settings.LANGUAGE_CODE == 'en-us':
            return self.name
        else:
            return OrganizationCategoryTranslation.objects.get(
                lang=settings.LANGUAGE_CODE, category=self).name

    @classmethod
    def category_logos_dict(cls):
        return {
            1: "culture-and-arts.png",
            2: "education.png",
            3: "environment.png",
            4: "health.png",
            5: "housing.png",
            6: "research.png",
            7: "self-help.png",
            8: "social-services.png",
            9: "sports-and-recreation.png",
            10: "emergency-aid-disaster-relief.png",
            11: "animal-protection.png",
            12: "community-development.png",
            13: "income-generation.png",
            14: "human-rights-promotion.png",
            15: "law-and-legal-services.png",
            16: "voluntarism-promotion.png",
            17: "promotion-of-civil-society-organizations.png",
            18: "fundraising-and-grant-making-organization.png",
            19: "peace-promotion.png",
            20: "cultural-exchange.png",
            21: "development-assistance.png",
        }

    @property
    def image(self):
        return "img/org_categories/{}".format(
            OrganizationCategory.category_logos_dict()[self.id])


class OrganizationCategoryTranslation(models.Model):
    name = models.CharField(max_length=320)
    slug = models.CharField(max_length=320)
    lang = models.CharField(max_length=10)
    category = models.ForeignKey(OrganizationCategory)

    def __unicode__(self):
        return self.name

    def save(self, *a, **kw):
        self.slug = slugify(self.name)
        return super(OrganizationCategoryTranslation, self).save(*a, **kw)

