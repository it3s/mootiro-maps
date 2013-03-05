# -*- coding: utf-8 -*-
import simplejson

from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext as _
from django.core.paginator import Paginator
from jsonfield import JSONField

from komoo_map.models import GeoRefModel
from authentication.models import User
from tags.models import TagField, EMPTY_TAG

from .utils import build_obj_from_dict, get_model_from_table_ref, to_json
from .relations import RELATIONS


class BaseModel(models.Model):
    """
    Base Model provides:
        - a DAO interface for abstracting de ORM
        - easy table references

    examples:
      ```
          class MyModel(BaseModel):
            pass

          obj = MyModel()
          obj.table_ref  # returns a reference like "app_label.class_name"

          MyModel.get_by_id(number)
          MyModel.filter_by(name='bla', other_data='ble')
          obj, created = MyModel.get_or_create(name='bla', other_data='ble')
      ```
    """

    class Meta:
        abstract = True

    @classmethod
    def _table_ref(cls):
        return '{}.{}'.format(cls._meta.app_label, cls.__name__)

    @property
    def table_ref(self):
        """ Returns a "app_label.class_name" string """
        return self._table_ref()

    @classmethod
    def get_by_id(cls, id):
        """ Get entry by ID or return None """
        try:
            obj = cls.objects.get(pk=id)
        except Exception:
            obj = None
        return obj

    @classmethod
    def filter_by(cls, **kwargs):
        """ filter by keyword arguments """
        return cls.objects.filter(**kwargs)

    @classmethod
    def get_or_create(cls, **kwargs):
        """ get if exists or create if don't. Returns: (obj, created) """
        return cls.objects.get_or_create(**kwargs)

    # utility json methods
    def to_json(self):
        if hasattr(self, 'to_dict'):
            return to_json(self.to_dict())
        else:
            raise Exception('No .to_dict() method defined')

    def from_json(self, data):
        if hasattr(self, 'from_dict'):
            self.from_dict(simplejson.loads(data))
        else:
            raise Exception('No .from_dict() method defined')


# =============================================================================
#  Generic Relations
#

class GenericRef(BaseModel):
    """ Generic Ref used for the GenericRelation Table """
    obj_table = models.CharField(max_length=1024)
    obj_id = models.IntegerField()

    def get_object(self):
        """ get the 'true' object from the reference """
        model = get_model_from_table_ref(self.obj_table)
        return model.objects.get(id=self.obj_id)

    @classmethod
    def get_reference_for_object(cls, obj):
        """ given a object, get the reference for it"""
        ref, created = cls.get_or_create(
                obj_table=obj.table_ref, obj_id=obj.id)
        return ref


class GenericRelation(BaseModel):
    """ Generic Relations Betwen any two objects"""
    obj1 = models.ForeignKey(GenericRef, related_name='relations_for_obj1')
    obj2 = models.ForeignKey(GenericRef, related_name='relations_for_obj2')

    relation_type = models.CharField(max_length=1024, null=True, blank=True)

    creation_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['creation_date', ]

    @classmethod
    def has_relation(cls, obj1, obj2):
        """ check if any two object has a relation """
        # TODO: CHANGE-ME to **not** build the references
        ref_obj1 = GenericRef.get_reference_for_object(obj1)
        ref_obj2 = GenericRef.get_reference_for_object(obj2)

        relations = GenericRelation.objects.filter(
            Q(obj1=ref_obj1, obj2=ref_obj2) |
            Q(obj1=ref_obj2, obj2=ref_obj1)
        )
        return relations.exists()

    @classmethod
    def add_relation(cls, obj1, obj2, relation_type=None):
        """ add (if dont exist) a relation betwen two objects """
        if not cls.has_relation(obj1, obj2):
            ref_obj1 = GenericRef.get_reference_for_object(obj1)
            ref_obj2 = GenericRef.get_reference_for_object(obj2)

            relation, created = GenericRelation.get_or_create(
                    obj1=ref_obj1, obj2=ref_obj2, relation_type=relation_type)

            return relation
        else:
            return None

    @classmethod
    def remove_relation(cls, obj1, obj2):
        """ add (if dont exist) a relation betwen two objects """
        rel = GenericRelation.objects.filter(
            Q(
                obj1__obj_id=obj1.id, obj1__obj_table=obj1.table_ref,
                obj2__obj_id=obj2.id, obj2__obj_table=obj2.table_ref,
            ) |
            Q(
                obj1__obj_id=obj2.id, obj1__obj_table=obj2.table_ref,
                obj2__obj_id=obj1.id, obj2__obj_table=obj1.table_ref,
            )
        )
        if rel.exists():
            rel.delete()
            return True
        return False


class _RelationsList(list):
    """ utility extended list for relations in RelationsField descriptor"""
    def __init__(self, descriptor, instance, queryset=None):
        self.descriptor = descriptor
        self.instance = instance
        self.qs = queryset

    def add(self, obj, relation_type=None):
        """ add relation with an object """
        return self.descriptor.add_relation(
                self.instance, obj, relation_type=relation_type)

    def remove(self, obj):
        """ remove relations with an object """
        self.descriptor.remove_relation(self.instance, obj)

    def paginated(self, page=1, per_page=10):
        """
        return a paginated relations.
        usage:
          obj.relations.paginated(per_page=20) # page 1, 20 items
          obj.relations.paginated(page=3, per_page=20) # from item 41 to 60
        """
        if self.qs:
            paginator = Paginator(self.qs, per_page)
            return self._build_list_from_queryset(
                    paginator.page(page).object_list)

        else:
            return self

    def filter_by_model(self, model):
        """
        filter relations by table_ref
        example:
          obj.relations
          # returns [(org1, ''), (resource,''), (org2, '')]
          obj.relations.filter_by_model(Organization)
          # returns [(org1, ''), (org2, '')]

        it is chainable. Ex:
            obj.relations.filter_by_model(Organization
                            ).paginated(page=2, per_page=5)
        """
        table_ref = model._table_ref()
        rel_obj = GenericRef.get_reference_for_object(self.instance)
        qs = GenericRelation.objects.filter(
            Q(obj1=rel_obj, obj2__obj_table=table_ref) |
            Q(obj2=rel_obj, obj1__obj_table=table_ref)
        )
        return self._build_list_from_queryset(qs)

    def _build_list_from_queryset(self, qs):
        """
        Given a GenericRelation queryset, build a list like:
          [
            (object_1, 'relation_type_with_1'),
            (object_2, 'relation_type_with_2')
          ]
        """
        relation_list = _RelationsList(self.descriptor, self.instance,
                queryset=qs)
        for rel in qs:
            if rel.obj1.obj_table == self.instance.table_ref and \
               rel.obj1.obj_id == self.instance.id:

                relation_list.append(
                    (rel.obj2.get_object(),
                     RELATIONS[rel.relation_type][0]
                            if rel.relation_type else '')
                )

            elif rel.obj2.obj_table == self.instance.table_ref and \
               rel.obj2.obj_id == self.instance.id:

                relation_list.append(
                    (rel.obj1.get_object(),
                     RELATIONS[rel.relation_type][1]
                            if rel.relation_type else '')
                )

            else:
                raise Exception('instance is not referenced in the relation')
                pass

        return relation_list


class RelationsField(object):
    """
    Relations descriptor.
    usage:
        ```
            class MyClass(models.Model):
                relations = RelationsField()

            obj = MyClass()
            obj.relations
            # returns []

            obj.relations = [
                (objA, 'relation_type1'),
                (objB, 'relation_type2')
            ]
            # creates and saves relations to object

            obj.relations
            # returns [(objA, 'relation_type1'), (objB, 'relation_type2')]

            obj.relations.add(objC, relation_type3)
            obj.relations.remove(objA)
            obj.relations
            # returns [(objB, 'relation_type2'), (objC, 'relation_type3')]

            obj.relations.paginate(page=1, num=10)
            obj.relations.filter_by_type('relation_type1')
        ```
    """
    def __get__(self, instance, owner):
        ref_obj = GenericRef.get_reference_for_object(instance)
        qs = GenericRelation.objects.filter(
                Q(obj1=ref_obj) | Q(obj2=ref_obj))

        relation_list = _RelationsList(self, instance, queryset=qs)
        return relation_list._build_list_from_queryset(qs)

    def __set__(self, instance, new_relations):
        # del old relations
        self.__delete__(instance)

        # create new tags
        for rel in new_relations:
            obj = rel[0] or None
            relation_type = rel[1] or None
            self.add_relation(instance, obj, relation_type)

    def __delete__(self, instance):
        ref_obj = GenericRef.get_reference_for_object(instance)
        GenericRelation.objects.filter(
            Q(obj1=ref_obj) | Q(obj2=ref_obj)
        ).delete()

    def add_relation(self, instance, obj, relation_type=None):
        GenericRelation.add_relation(
            instance, obj, relation_type=relation_type)

    def remove_relation(self, instance, obj):
        if obj:
            return GenericRelation.remove_relation(instance, obj)


# =============================================================================
# Common Objects
#


class GeoRefObject(GeoRefModel, BaseModel):
    """
    Common objects base model.

    Fields:
        name: object identifier
        description: longer description of the object
        creator: user who created this content
        creation_date: datetime when the content was created
        last_editor: last user who edited this content
        last_update: datetime for the last edition
        extra_data: utility field which holds a json with extra data (used for
            object conversion. For example: when we change a Organization to a
            Resource, we want to preserve the organization specific data in
            this field)
        tags: tags array for the content (provided by TagsMixin)

    Methods:
        to_dict: return a dict representation for the common attributes

    """
    name = models.CharField(max_length=512)
    description = models.TextField()

    creator = models.ForeignKey(User, editable=False, null=True,
                        related_name='created_%(class)s')
    creation_date = models.DateTimeField(auto_now_add=True)
    last_editor = models.ForeignKey(User, editable=False, null=True,
                        blank=True, related_name='last_edited_%(class)s')
    last_update = models.DateTimeField(auto_now=True)

    extra_data = JSONField(null=True, blank=True)

    tags = TagField()

    relations = RelationsField()

    def __unicode__(self):
        return unicode(self.name)

    def to_dict(self):
        return {
            'name': self.name,
            'description': self.description,
            'creator': self.creator,
            'creation_date': self.creation_date,
            'last_editor': self.last_editor,
            'last_update': self.last_update,
            'tags': self.tags,
            'extra_data': self.extra_data,
        }

    def postpone_attr(self, key, val):
        self._postponed = getattr(self, '_postponed', [])
        self._postponed.append((key, val))

    def from_dict(self, data, complete_object=False, *args, **kwargs):
        self._postponed = getattr(self, '_postponed', [])
        attrs = [
            'id', 'name', 'description', 'last_editor', 'creation_date',
            'last_update', 'extra_data', 'creator']
        update_attrs = [attr for attr in attrs[::] if not attr in
                ['id', 'creator', 'last_update', 'creation_date']]
        insert_attrs = [attr for attr in attrs[::] if not attr in
                ['id', 'last_editor', 'last_update', 'creation_date']]

        if complete_object:
            keys = attrs
        elif getattr(self, 'id', None):
            keys = update_attrs
        else:
            keys = insert_attrs
            if data.get('creation_date', None):
                self.postpone_attr('creation_date', data['creation_date'])

        [
            self.postpone_attr(attr, val) for attr, val in
                [('tags', data.get('tags', EMPTY_TAG)), ]
        ]

        date_keys = ['creation_date', 'last_update']
        build_obj_from_dict(self, data, keys, date_keys)

    def is_valid(self):
        self.errors = {}
        validates = True
        require = ['otype', 'name', 'creator']
        for field in require:
            if not getattr(self, field, None):
                valid, self.errors[field] = False, _('Required field')
        return validates

    def save(self, *args, **kwargs):
        r = super(GeoRefObject, self).save(*args, **kwargs)
        if self.id and hasattr(self, '_postponed'):
            for item in self._postponed:
                setattr(self, item[0], item[1])
        return r
