# -*- coding: utf-8 -*-
from django.db import models
from django.db import IntegrityError


COMMON_NAMESPACE = 'common'

EMPTY_TAG = {COMMON_NAMESPACE: []}


class TagNamespace(models.Model):
    """ Namespace for Tags """
    name = models.CharField(max_length=128, unique=True)

    def __unicode__(self):
        return self.name

    @classmethod
    def add(cls, namespace):
        namespace, created = TagNamespace.objects.get_or_create(
                        name=namespace)
        return namespace


class Tag(models.Model):
    """ Tags with namespace """
    name = models.CharField(max_length=128)
    namespace = models.ForeignKey(TagNamespace)

    @classmethod
    def add(cls, tag_name, namespace=COMMON_NAMESPACE):
        """ add a tag given its 'name'. Tags are unique by namespace """
        tag_namespace, created = TagNamespace.objects.get_or_create(
                        name=namespace)
        tag, created = cls.objects.get_or_create(
                        name=tag_name, namespace=tag_namespace)
        return tag

    @classmethod
    def get_by_name(cls, tag_name, namespace=COMMON_NAMESPACE):
        try:
            tag = Tag.objects.get(name=tag_name, namespace__name=namespace)
        except Exception:
            tag = None
        return tag

    def save(self, *args, **kwargs):
        try:
            namespace = self.namespace
        except:
            namespace = None
        if not namespace:
            tag_namespace, cr = TagNamespace.objects.get_or_create(
                    name=COMMON_NAMESPACE)
            self.namespace = tag_namespace

        ts = Tag.objects.filter(
                name=self.name, namespace=self.namespace)
        if ts.exists():
            raise IntegrityError(
                    'Tag with this name and namespace already exists')
        return super(Tag, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.name


class TaggedObject(models.Model):
    """ Tagged Generic Objects """
    tag = models.ForeignKey(Tag)
    object_id = models.IntegerField()
    object_table = models.CharField(max_length=512)

    @classmethod
    def get_tags_for_object(cls, obj):
        """ get all tags for and object """
        return [
            tagged_obj.tag for tagged_obj in TaggedObject.objects.filter(
                object_id=getattr(obj, 'id', None),
                object_table='{}.{}'.format(obj._meta.app_label,
                    obj.__class__.__name__)
            )]

    @classmethod
    def get_tags_for_object_by_namespace(cls, obj, namespace=COMMON_NAMESPACE):
        """ get all tags for and object by tag namespace """
        return [
            tagged_obj.tag for tagged_obj in TaggedObject.objects.filter(
                object_id=getattr(obj, 'id', None),
                object_table='{}.{}'.format(obj._meta.app_label,
                    obj.__class__.__name__),
                tag__namespace__name=namespace
        )]

    @classmethod
    def add_tag_to_object(cls, tag, obj):
        obj, created = TaggedObject.objects.get_or_create(
            object_id=getattr(obj, 'id', None),
            object_table='{}.{}'.format(obj._meta.app_label,
                obj.__class__.__name__),
            tag=tag)


class _TagList(dict):
    """ utility extended list for tags in TagField descriptor"""
    def __init__(self, descriptor, instance):
        self.descriptor = descriptor
        self.instance = instance

    def add(self, tag, namespace=COMMON_NAMESPACE):
        return self.descriptor.add_tag(self.instance, tag, namespace=namespace)

    def remove(self, tag, namespace=COMMON_NAMESPACE):
        self.descriptor.remove_tag(self.instance, tag, namespace=namespace)

    def by_namespace(self, namespace):
        return self.descriptor.get_tags_by_namespace(self.instance, namespace)


class TagField(object):
    """
    Tag-like behavior descriptor. It treats the TagField attribute like a
    list, but implictly makes all the necessary database queries.
    The constructor uses an optional 'namespace' attribute to specialize
    the tags. The default namesmpace is 'tag'
    usage:
        class MyClass(models.Model):
            tags = TagField()

        obj = MyClass()
        obj.tags
        # returns {'common': []}

        obj.tags = {'common': ['tag A', 'tag B']}
        # creates and saves tags to object

        obj.tags
        # returns {'common': ['tag A', 'tag B']}

        obj.tags.add('tag C')
        obj.tags.remove('tag A')
        obj.tags
        # returns {'common': ['tag B', 'tag C']}

        obj.tags.by_namespace('target_audience')
        # returns []

        obj.tags.add('tag C', namespace='target_audience')
        # Now we have a 'tag C' for the default namespace 'common' and other
        # for the 'target_audience' namespace
    """
    def __get__(self, instance, owner):
        tag_list = _TagList(self, instance)
        tag_list[COMMON_NAMESPACE] = []
        for tag in TaggedObject.get_tags_for_object(instance):
            if not tag.namespace.name in tag_list:
                tag_list[tag.namespace.name] = [tag.name, ]
            else:
                tag_list[tag.namespace.name].append(tag.name)
        return tag_list

    def __set__(self, instance, new_tags):
        # del old tags
        self.__delete__(instance)

        for namespace, tag_list in new_tags.iteritems():
            for tag in tag_list:
                self.add_tag(instance, tag, namespace=namespace)

    def __delete__(self, instance):
        tags = [
            tagged_obj for tagged_obj in TaggedObject.objects.filter(
                object_id=getattr(instance, 'id', None),
                object_table='{}.{}'.format(instance._meta.app_label,
                    instance.__class__.__name__)
        )]
        for tag in tags:
            tag.delete()

    def add_tag(self, instance, tag, namespace=COMMON_NAMESPACE):
        tag_obj = Tag.add(tag, namespace=namespace)
        TaggedObject.add_tag_to_object(tag_obj, instance)
        return tag_obj

    def remove_tag(self, instance, tag, namespace=COMMON_NAMESPACE):
        if isinstance(tag, basestring):
            tag = Tag.get_by_name(tag, namespace=namespace)
        elif not isinstance(tag, Tag):
            tag = None

        if tag:
            TaggedObject.objects.filter(
                    object_id=getattr(instance, 'id', None),
                    object_table='{}.{}'.format(instance._meta.app_label,
                        instance.__class__.__name__),
                    tag=tag
            ).delete()

    def get_tags_by_namespace(self, instance, namespace):
        tag_namespace, cr = TagNamespace.objects.get_or_create(name=namespace)
        tags = [
            tagged_obj.tag.name for tagged_obj in TaggedObject.objects.filter(
                object_id=getattr(instance, 'id', None),
                object_table='{}.{}'.format(instance._meta.app_label,
                    instance.__class__.__name__),
                tag__namespace=tag_namespace
        )]
        return tags

