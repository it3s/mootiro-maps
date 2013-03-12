# -*- coding: utf-8 -*-
import unittest
import pymongo
import model
from model import ModelMCS, ModelCursor, Model
from settings import Testing


class Counter:
    # utility class to use with connexions testing
    num = 0

    @classmethod
    def inc(cls):
        cls.num += 1

    @classmethod
    def ensure_0(cls):
        cls.num = 0


class CounterTest(unittest.TestCase):
    # test the utility test class -> TestInception
    def setUp(self):
        self.counter = Counter()
        self.counter.ensure_0()

    def tearDown(self):
        del self.counter

    def test_counter_creation(self):
        self.assertEqual(self.counter.num, 0)

    def test_counter_inc(self):
        self.counter.inc()
        self.assertEqual(self.counter.num, 1)

    def test_multiple(self):
        counter1 = Counter()
        counter2 = Counter()
        Counter.ensure_0()
        counter1.inc()
        counter2.inc()
        self.assertEqual(counter1.num, counter2.num)
        self.assertEqual(Counter.num, 2)
        del counter1
        del counter2


class ModelModuleTests(unittest.TestCase):

    def test_connect(self):
        connexions = Counter()
        Counter.ensure_0()
        config = type('ConfigMock', (), {})()

        # mocking a model
        DummyModel = type('ModelMock', (), {})

        def mocked_connect(test):
            def _connect(conf):
                connexions.inc()
                test.assertIs(conf, config)
            return _connect

        model1 = DummyModel()
        model1.connect = mocked_connect(self)

        model2 = DummyModel()
        model2.connect = mocked_connect(self)

        model._models_registry = set([model1, model2])
        model.connect(config)
        self.assertEqual(connexions.num, 2)


class MetaModelTests(unittest.TestCase):
    def test_model_registration(self):
        # isolate test
        model._models_registry = set()

        class NewModel(object):
            __metaclass__ = ModelMCS

        # NewModel should be registered
        self.assertEqual(len(model._models_registry), 1)

        self.assertEqual(list(model._models_registry)[0], NewModel)
        self.assertEqual(NewModel.__metaclass__, ModelMCS)

        class AnotherModel(NewModel):
            pass

        self.assertEqual(len(model._models_registry), 2)


class ModelCursorTests(unittest.TestCase):

    class ModelMock:
        def __init__(self, *a, **kw):
            if len(a) > 0 and isinstance(a[0], dict):
                self.obj = a[0]
            else:
                self.obj = None

    @classmethod
    def setUpClass(cls):
        cls.db = Testing.get_db()
        collection = cls.db.cursor_test
        cls.ModelMock.collection = collection

    def setUp(self):
        self.model = self.ModelMock()
        self.cursor = ModelCursor(self.model.__class__)

    def tearDown(self):
        self.db.drop_collection('cursor_test')

    def test_pymongo_cursor_wrapping(self):
        self.assertIsInstance(self.cursor.find().mongo_cursor,
                    pymongo.cursor.Cursor)

    def test_cursor_next_returns_model_instance(self):
        self.model.collection.save({'name': 'model1'})

        self.assertEqual(self.cursor.find().next().__class__,
                self.model.__class__)

    def test_iteration_returns_model_instance(self):
        dict1 = {'name': 'model1'}
        dict2 = {'name': 'model2'}
        self.model.collection.save(dict1)
        self.model.collection.save(dict2)

        for m in self.cursor.find():
            self.assertIsInstance(m, self.ModelMock)

    def test_first_return_0_index_value_from_find(self):
        dict1 = {'name': 'model1'}
        dict2 = {'name': 'model2'}
        self.model.collection.save(dict1)
        self.model.collection.save(dict2)

        self.assertIsInstance(self.cursor.find().first(), self.ModelMock)
        self.assertEqual(self.cursor.find().first().obj['name'], dict1['name'])

    def test_find(self):
        model_dict = {'name': 'find test'}
        self.model.collection.save(model_dict)

        self.assertIsInstance(
                self.cursor.find({'name': 'find test'}).next(),
                self.model.__class__)

        self.assertEqual(
                self.cursor.find({'name': 'find test'}).first().obj['name'],
                model_dict['name'])

    def test_count(self):
        model_dict = {'name': 'find test'}
        self.model.collection.save(model_dict)

        self.assertEqual(
                self.cursor.find({'name': 'find test'}).count(), 1)


class ModelConnectTests(unittest.TestCase):

    def setUp(self):
        class MyModel(Model):
            collection_name = 'model_test'

        self.model = MyModel()

    def test_connect_from_str(self):
        db_conf = Testing.MONGO_DBNAME

        self.assertIs(self.model.collection, None)
        self.model.connect(db_conf)

        self.assertEqual(self.model.collection.name, 'model_test')
        self.assertIsInstance(self.model.collection,
                pymongo.collection.Collection)

    def test_connect_from_class(self):
        class conf(object):
            MONGO_DBNAME = Testing.MONGO_DBNAME

        db_conf = conf
        self.assertIs(self.model.collection, None)
        self.model.connect(db_conf)

        self.assertEqual(self.model.collection.name, 'model_test')
        self.assertIsInstance(self.model.collection,
                pymongo.collection.Collection)

    def test_connect_from_method(self):
        class conf(object):
            @classmethod
            def get_db(cls):
                return Testing.get_db()

        db_conf = conf
        self.assertIs(self.model.collection, None)
        self.model.connect(db_conf)

        self.assertEqual(self.model.collection.name, 'model_test')
        self.assertIsInstance(self.model.collection,
                pymongo.collection.Collection)

    def test_raises_error_when_model_has_no_collection_name(self):
        db_conf = Testing.MONGO_DBNAME

        class WrongModel(Model):
            collection_name = ''
        self.model = WrongModel()

        with self.assertRaises(Exception):
            self.model.connect(db_conf)

    def test_raises_error_when_config_is_not_valid(self):
        db_conf = 986590

        with self.assertRaises(Exception):
            self.model.connect(db_conf)


class ModelTestBase(unittest.TestCase):
    """This is a base class for the the tests below"""

    class ModelTest(Model):
        collection_name = 'model_test'

    @classmethod
    def setUpClass(cls):
        cls.ModelTest.connect(Testing)
        cls.ModelTest.collection.remove({})

    def tearDown(self):
        self.ModelTest.collection.remove({})


class ModelInstanceTests(ModelTestBase):
    def test_model_instance_empty_data(self):
        model = self.ModelTest()
        self.assertEqual(model._data, {})

    def test_model_instance_dict_data(self):
        data = {'a': 1, 'b': 'bbbbbb'}
        model = self.ModelTest(data)
        self.assertEqual(model._data, data)

    def test_model_instance_kwargs_data(self):
        data = {'a': 1, 'b': 'bbbbbb'}
        model = self.ModelTest(a=1, b='bbbbbb')
        self.assertEqual(model._data, data)

    def test_model_instance_hibrid_data(self):
        data = {'a': 1, 'b': 'bbbbbb'}
        model = self.ModelTest({'a': 1}, b='bbbbbb')
        self.assertEqual(model._data, data)

    def test_model_instance_access_data_from_dot_notation(self):
        model = self.ModelTest({'a': 1}, b='bbbbbb')
        self.assertEqual(model.a, 1)
        self.assertEqual(model.b, 'bbbbbb')
        self.assertEqual(model.get('a'), model.a)
        self.assertEqual(model.get('b'), 'bbbbbb')

    def test_set(self):
        model = self.ModelTest()
        with self.assertRaises(ValueError):
            model.set()
        model.set({'a': 1})

        model2 = self.ModelTest()
        model2.set(a=1)

        self.assertEqual(model._data, model2._data)

        model.set({'a': 1, 'b': 2})
        self.assertEqual(model.get('a'), 1)
        self.assertEqual(model._data['b'], 2)
        self.assertEqual(model._data, {'a': 1, 'b': 2})

        model.set(c=3, d=4)
        self.assertEqual(model.get('c'), 3)
        self.assertEqual(model.d, 4)

    def test_get(self):
        model = self.ModelTest()
        model.set(a=1)
        self.assertEqual(model.get('a'), 1)
        self.assertEqual(model.a, 1)

        model._data['a'] = 2
        self.assertEqual(model.get('a'), 2)

        self.assertIs(model.get('b'), None)
        with self.assertRaises(AttributeError):
            model.b

    def test_proxy_setitem_to_data_dict(self):
        model = self.ModelTest(a=1)
        model.set({'b': 2, 'c': 3})
        self.assertEqual(model._data, {'a': 1, 'b': 2, 'c': 3})
        model.set({'c': 4})
        self.assertEqual(model._data['c'], 4)
        self.assertEqual(model.c, 4)

    def test_data_property_getter(self):
        model = self.ModelTest({'a': 1}, b=2)
        model.set({'c': 3})
        self.assertEqual(model._data, {'a': 1, 'b': 2, 'c': 3})
        self.assertEqual(model.get('a'), 1)
        self.assertEqual(model.b, 2)

    def test_data_property_setter(self):
        model = self.ModelTest()
        model.set({'a': 1, 'b': 2, 'c': 3})
        self.assertEqual(model._data, {'a': 1, 'b': 2, 'c': 3})
        model.set({'a': 2, 'd': 4})
        self.assertEqual(model._data, {'a': 2, 'b': 2, 'c': 3, 'd': 4})


class ModelUpsertTests(ModelTestBase):

    def test_insert(self):
        model = self.ModelTest(a=1, b=2)
        model.upsert()
        self.assertEqual(self.ModelTest.collection.find().count(), 1)
        self.assertTrue(model._id)
        self.assertIn('_id', model._data.keys())
        self.assertTrue(self.ModelTest.collection.find({'a': 1, 'b': 2}))

    def test_update(self):
        model = self.ModelTest(a=1, b=2)
        model.upsert()
        retrieved_model = self.ModelTest.collection.find_one({'a': 1})
        self.assertEqual(retrieved_model['b'], model.b)

        model.set(b=4)
        model.upsert()
        self.assertEqual(self.ModelTest.collection.find({'a': 1}).count(), 1)

        retrieved_model = self.ModelTest.collection.find_one({'a': 1})
        self.assertEqual(retrieved_model['b'], 4)
        self.assertEqual(retrieved_model['_id'], model._id)

    def test_partial_update(self):
        model = self.ModelTest(a=1, b=2, c=3)
        model.upsert()

        retrieved_doc = self.ModelTest.collection.find_one(
                {'a': 1, 'b': 2, 'c': 3})

        _id = retrieved_doc['_id']

        model = self.ModelTest({'_id': _id})
        model.set(a=5)
        model.set(b=6)
        self.assertNotIn('c', model._data)
        model.upsert()

        retrieved_doc = self.ModelTest.collection.find_one({'_id': _id})
        self.assertEqual(retrieved_doc,
                {'a': 5, 'b': 6, 'c': 3, '_id': _id})


class ModelRemoveTests(ModelTestBase):

    def test_raises_error_when_no_id(self):
        d = {'a': 1, 'b': 2}
        model = self.ModelTest(d)
        self.assertFalse(hasattr(model, '_id'))
        with self.assertRaises(ValueError):
            model.remove()

    def test_remove_object(self):
        model1 = self.ModelTest({'num': 1})
        model1.upsert()

        model2 = self.ModelTest({'num': 2})
        model2.upsert()

        self.assertTrue(hasattr(model1, '_id'))
        self.assertTrue(hasattr(model2, '_id'))

        self.assertEqual(self.ModelTest.collection.find().count(), 2)

        self.assertTrue(model1.remove())

        self.assertEqual(self.ModelTest.collection.find().count(), 1)


class ModelFindTests(ModelTestBase):
    def setUp(self):
        super(ModelFindTests, self).setUp()
        model1 = self.ModelTest({'num': 1})
        model1.upsert()
        model2 = self.ModelTest({'num': 2})
        model2.upsert()
        model3 = self.ModelTest({'num': 3})
        model3.upsert()

    def test_find_all(self):
        self.assertEqual(self.ModelTest.find().count(), 3)

        for m in self.ModelTest.find():
            self.assertIsInstance(m, self.ModelTest)

    def test_find_query(self):
        query = self.ModelTest.find({
            'num': {
                '$lt': 3
            }
        })
        self.assertEqual(query.count(), 2)

        for model in query:
            self.assertIsInstance(model, self.ModelTest)
            self.assertIn(model.num, [1, 2])


class ModelToDictTests(unittest.TestCase):
    def test_no_structure(self):
        class NoStructModel(Model):
            collection_name = 'model_test'

        NoStructModel.connect(Testing)
        NoStructModel.collection.remove({})

        model = NoStructModel(a=1, b=2, c=3)
        self.assertEqual(model.to_dict(), {'a': 1, 'b': 2, 'c': 3})

    def test_strucutured_model(self):
        class Person(Model):
            collection_name = 'person_test'
            structure = {
                'name': unicode,
                'desc': 'dynamic',
                'age': int,
            }

        model = Person(name='John Doe', age=35, desc='no one', bla='ble')
        self.assertNotIn('bla', model.to_dict().keys())
        self.assertEqual(model.to_dict(), dict(
            name=u'John Doe',
            age=35,
            desc='no one'
        ))
        self.assertNotEqual(model.to_dict(), model._data)
        self.assertIn('bla', model._data)

    def test_id_on_inserted_model(self):
        class Person(Model):
            collection_name = 'person_test'
            structure = {
                'name': unicode,
                'desc': 'dynamic',
                'age': int,
            }
        Person.connect(Testing)
        Person.collection.remove({})

        model = Person(name='John Doe', age=35, desc='no one', bla='ble')
        _id = model.upsert()
        self.assertTrue(model.get('_id'))
        self.assertEqual(model._id, _id)

        self.assertIn('_id', model.to_dict())
        self.assertEqual(model.to_dict(), dict(
            name=u'John Doe',
            age=35,
            desc='no one',
            _id=_id
        ))

    def test_to_dict_without_id(self):
        # with structure
        class Person(Model):
            collection_name = 'person_test'
            structure = {
                'name': unicode,
                'desc': 'dynamic',
                'age': int,
            }
        Person.connect(Testing)
        Person.collection.remove({})

        model = Person(name='John Doe', age=35, desc='no one', bla='ble')
        model.upsert()

        self.assertIn('_id', model._data)
        self.assertNotIn('_id', model.to_dict(with_id=False))
        self.assertIn('_id', model.to_dict())

        # without structure
        class NoStructPerson(Model):
            collection_name = 'person_test'

        new_model = NoStructPerson(model.to_dict())

        self.assertIn('_id', new_model._data)
        self.assertNotIn('_id', new_model.to_dict(with_id=False))
        self.assertIn('_id', new_model.to_dict())

    def test_validators(self):
        def older_than_18(age):
            return age > 18

        class Adult(Model):
            structure = {
                'name': unicode,
                'age': int
            }
            validators = {
                'age': [older_than_18, ]
            }

        ze = Adult(name=u'Zé', age='38')
        self.assertTrue(ze.to_dict())

        zezinho = Adult(name='zezinho', age=11)
        with self.assertRaises(ValueError):
            zezinho.to_dict()


if __name__ == '__main__':
    unittest.main()

