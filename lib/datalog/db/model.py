# -*- coding: utf-8 -*-
"""
db.model is a thin layer over MongoDB python driver (pymongo).
Its provides some syntatic-sugar for avoiding common mistakes like typos on
collection names and so.
All classes which inherits from Model should easily access the underlying
pymongo's bare Collection. Its does so via the collection attribute.
It also provide some methods to ensure validations, structure
(not obstrusively, i.e., you can have extra parameters aside from the
strucuture, this makes sense since we are dealing with a schemaless DB), and
simple queries.

"""
import pymongo
import logging
from copy import deepcopy

logging.basicConfig(level=logging.DEBUG)


# internal set for registering subclasses of Model
_models_registry = set()


def connect(config):
    """
    This method is used to automatically connect all registered sub-classes
    from Model to a proper mongodb connection.


    Parameters:
      :config: a config class with MONGO_DBNAME or
               a config class with .get_db() method or
               a string with database_name

    """
    for model in _models_registry:
        model.connect(config)


class ModelMCS(type):
    def __new__(mcs, name, bases, attrs):
        new_cls = super(ModelMCS, mcs).__new__(mcs, name, bases, attrs)
        if name != 'Model':
            _models_registry.add(new_cls)
        return new_cls


class ModelCursor(object):
    """
    ModelCursor is a simple wrapper over pymongo.cursor.Cursor.
    Its used internally on Model queries (and should be only used internally).

    All it does is, for some special query methods in the model, delegate to
    pymongo's cursor and wrapps the returned dict into a model instance or
    enable chaining methods.

    Methods:
      :find:  delegates a query to mongodb.

      :first:  used to retrieve the first result from a query result.

      :count:  return the number of result for the query

    """

    def __init__(self, model, *a, **kw):
        self.model = model

    def __iter__(self):
        return self

    def next(self):
        out = self.mongo_cursor.next()
        return self.model(out)

    def find(self, *args, **kwargs):
        """
        Makes a .find() on mongoDB with the very same parameters as pymongo
        Returns itself for chaining with other calls.

        For more info on parameters see:
        http://api.mongodb.org/python/current/api/pymongo/collection.html

        """
        self.mongo_cursor = pymongo.cursor.Cursor(self.model.collection,
                                                  *args, **kwargs)
        return self

    def first(self):
        """
        returns a model instance to the first result from the
        query (made before)
        """
        out = self.mongo_cursor[0]
        return self.model(out)

    def count(self):
        """ returns the query results count. """
        return self.mongo_cursor.count()


class Model(object):
    """
    This class should be inherited from all your models.
    It must have a collection_name class attribute with a string containing
    the name of the collection.

    """
    __metaclass__ = ModelMCS
    collection = None

    def __init__(self, *args, **kw):
        """
        The model constructor accepts data form a dictionary or any number of
        keyword arguments.
        It builds an internal data dict _data which holds all attributes.

        examples:

            model = MyModel({'a': 1, 'b': 2})
            model = MyModel(a=1, b=2)
            model = MyModel({'a': 1}, b=2)
            # they all build the same data atributes.

        """
        self._data = {}
        if len(args) > 0 and isinstance(args[0], dict):
            for field, value in args[0].iteritems():
                self._data[field] = value
        if kw:
            for field, value in kw.iteritems():
                self._data[field] = value

    def set(self, attrs={}, *a, **kw):
        """
        Set one or more data values.
        We can pass a dict containing the data to be set on the attrs
        parameter, or we can provide the data via keyword arguments.
        example:

                model = SomeModel()
                model.set({'name': 'John Doe'})
                model.set(name='John Doe')  # has the same effect


        parameters:
            :attrs: a dict containing the data to be set
            :kwargs: you can any number of keyword arguments

        """
        if attrs and isinstance(attrs, dict):
            self._data.update(attrs)
        elif kw:
            self._data.update(kw)
        else:
            raise ValueError(
                'You must provide either a attrs dict or keyword arguments')

    def get(self, attr):
        """
        Return the corresponding _data value
        On __getattr__ we have  syntatic sugar for acessing these value with
        dot notaion.
        example:

                model = SomeModel(name='John Doe')

                model.get('name') == model.name  # both return 'John Doe'


        Parameters:
            :attr: the attribute name

        """
        return self._data.get(attr, None)

    def __getattr__(self, attr):
        # syntatic sugar for acessing the _data attribute.
        # see docs for the .get method
        if not attr in self._data:
            raise AttributeError()
        return self._data.get(attr, None)

    @classmethod
    def connect(cls, db_conf):
        """
        This method connects the model to the database and instantiate the
        collection class attribute with a pymongo.collection.Collection
        given the collection_name

        Parameters:
          :db_conf:  a config class with MONGO_DBNAME or
                     a config class with .get_db() method or
                    a string with database_name

        """
        if not cls.collection_name:
            raise Exception('You must provide a collection name')

        if isinstance(db_conf, (str, unicode)):
            logging.debug('setting db from str/unicode')
            _cx = pymongo.Connection(safe=True, max_pool_size=20)
            _db = _cx[db_conf]
            cls.collection = _db[cls.collection_name]

        elif hasattr(db_conf, 'get_db'):
            logging.debug('Setting db from config.get_db')
            cls.collection = db_conf.get_db()[cls.collection_name]
        elif hasattr(db_conf, 'MONGO_DBNAME'):
            logging.debug('setting db from config.MONGO_DBNAME')
            _cx = pymongo.Connection(safe=True, max_pool_size=20)
            _db = _cx[db_conf.MONGO_DBNAME]
            cls.collection = _db[cls.collection_name]
        else:
            raise Exception('Could not set database properly')

    def upsert(self):
        """
        Method for inserting and updating a documment.
        If your class don't have an _id property it inserts a new record on
        the collection and automatically set the _id attribute on the model.
        In the other case, where you have an _id property it will make a
        **partial** update,i.e., intead of replacing the document it will only
        update the document with the data property fields.
        """
        if getattr(self, '_id', None):
            data_ = self.to_dict(with_id=False)
            r = self.collection.update(
                {'_id': self._id},
                {'$set': data_},
                safe=True)
        else:
            r = self.collection.insert(self._data)
            self._id = r
        return r

    def remove(self):
        """
        Removes the model from the collection. This method is safer than the
        collection.remove(model_data) because on the collecton method,
        if you pass a empty model_data the mongodb will happily remove all
        your collection data.
        This method remove a object given its _id, i.e., raises a ValueError
        if the model dont has the property _id.
        Return True if the object got successfuly removed.
        """
        if getattr(self, '_id', None):
            self.collection.remove({'_id': self._id})
            return True
        else:
            raise ValueError(
                    'We only can remove a objects which has and _id property')

    @classmethod
    def find(cls, *args, **kwargs):
        """proxy to ModelCursor.find"""
        cursor = ModelCursor(cls)
        return cursor.find(*args, **kwargs)

    def to_dict(self, with_id=True):
        """
        Returns a dict with the model data. Differently form the .data attr,
        this method coerces the data to a expected structure (from the
        structure class attribute) and validates it given a validators
        class atrribute.

        Parameters:
            :with_id: (default=True)
                Determines if the output dict will have the _id attribute

        example:

            Given the code below

                def older_than_18(val):
                    return val > 18

                class Adult(Model):
                    structure = {
                        'name': unicode
                        'age': int
                        'desc': unicode
                    }

                    validators = {
                        'age': [older_than_18, ]
                    }

                adult = Adult({
                    'name': 'Anderson',
                    'age': '25',
                    'desc': 'programmer',
                    'bla': 'ble'
                })

            the data attribute would give:
                {
                    'name': 'Anderson',
                    'age': '25',
                    'desc': 'programmer',
                    'bla': 'ble'
                }

            on the other hand, the to_dict attribute would give:
                {
                    'name': u'Anderson'
                    'age': 25,
                    'desc': u'programmer'
                }
            If we pass a age lesser than 18, we receive a ValueError

        If we don't have a structure it only returns the raw _data dictionary

        If one field strucuture type is 'dynamic', then no coercion will be
        made on that field.

        """
        data_dict = {}

        # coercions
        structure = getattr(self, 'structure', {})
        if structure:
            for field, _type in structure.iteritems():
                val = self._data[field] if _type == 'dynamic' \
                      else _type(self._data[field])
                data_dict[field] = val
        else:
            data_dict = deepcopy(self._data)

        # validations
        for field, validations in getattr(self, 'validators', {}).iteritems():
            for validator in validations:
                if not validator(data_dict[field]):
                    raise ValueError(
                        'Ilegal Value for field {} on validator {}'.format(
                            field, validator))

        # with or without _id
        if with_id and not '_id' in data_dict and '_id' in self._data:
            data_dict['_id'] = self._data['_id']
        elif not with_id and '_id' in data_dict:
            del data_dict['_id']

        return data_dict

