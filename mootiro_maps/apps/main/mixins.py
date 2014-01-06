# -*- coding: utf-8 -*-
import simplejson

from django.db import models

from .utils import to_json


class BaseModel(models.Model):
    """Base Model providing a DAO interface for abstracting of ORM and an easy
    table reference.

    Usage:
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
        """Return a "app_label.class_name" string."""
        return self._table_ref()

    @classmethod
    def get_by_id(cls, id):
        """Get entry by ID or return None."""
        try:
            obj = cls.objects.get(pk=id)
        except Exception:
            obj = None
        return obj

    @classmethod
    def filter_by(cls, **kwargs):
        """Filter by keyword arguments."""
        return cls.objects.filter(**kwargs)

    @classmethod
    def create(cls, **kwargs):
        """create an object"""
        return cls.objects.create(**kwargs)

    @classmethod
    def get_or_create(cls, **kwargs):
        """Get the object if exists or create if don't.

        Returns a tuple of format (obj, created)

        """
        return cls.objects.get_or_create(**kwargs)

    # utility json methods
    def to_json(self):
        """Create json representation."""
        if hasattr(self, 'to_dict'):
            return to_json(self.to_dict())
        else:
            raise Exception('No .to_dict() method defined')

    def from_json(self, data):
        """Fill the object attributes using the json values."""
        if hasattr(self, 'from_dict'):
            self.from_dict(simplejson.loads(data))
        else:
            raise Exception('No .from_dict() method defined')
