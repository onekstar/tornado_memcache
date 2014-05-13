#coding:utf-8
import uuid
from base import BaseTestCase
from tornado.testing import gen_test
from client import Client

class ClientTestCase(BaseTestCase):

    @gen_test
    def test_set(self):
        'test set cache'

        client = Client(['127.0.0.1:11211'])
        for value in ('abc', u'中国', 5, 5l): 
            key = uuid.uuid4().hex
            res = yield client.set(key, value, 5)
            self.assertEqual(res, True)

    @gen_test
    def test_get_when_not_exist(self):
        'test get cache when cache do not exist'

        key = uuid.uuid4().hex
        client = Client(['127.0.0.1:11211'])
        res = yield client.get(key)
        self.assertEqual(res, None)

    @gen_test
    def test_get_when_exist(self):
        'test get cache when cache do not exist'

        key = uuid.uuid4().hex
        client = Client(['127.0.0.1:11211'])
        yield client.set(key, 'value', 5)
        res = yield client.get(key)
        self.assertEqual(res, 'value')
    
    @gen_test
    def test_incr_when_cache_not_exist(self):
        'test incr when cache not exist'

        key = uuid.uuid4().hex
        client = Client(['127.0.0.1:11211'])
        res = yield client.incr(key, delta=2)
        self.assertEqual(res, None)

    @gen_test
    def test_incr(self):
        'test incr'

        key = uuid.uuid4().hex
        value = 2
        delta = 2
        client = Client(['127.0.0.1:11211'])
        yield client.set(key, value, 5)
        res = yield client.incr(key, delta=delta)
        self.assertEqual(res, value+delta)
    
    @gen_test
    def test_decr_when_cache_not_exist(self):
        'test incr when cache not exist'

        key = uuid.uuid4().hex
        client = Client(['127.0.0.1:11211'])
        res = yield client.decr(key, delta=2)
        self.assertEqual(res, None)

    @gen_test
    def test_decr(self):
        'test decr'

        key = uuid.uuid4().hex
        value = 2
        delta = 2
        client = Client(['127.0.0.1:11211'])
        yield client.set(key, value, 5)
        res = yield client.decr(key, delta=delta)
        self.assertEqual(res, value-delta)
    
    @gen_test
    def test_delete_when_not_exist(self):
        
        client = Client(['127.0.0.1:11211'])
        key = uuid.uuid4().hex
        res = yield client.delete(key)
        self.assertEqual(res, True)

    @gen_test
    def test_delete_when_exist(self):
        
        client = Client(['127.0.0.1:11211'])
        key = uuid.uuid4().hex
        yield client.set(key, 'value', 5)
        res = yield client.delete(key)
        self.assertEqual(res, True)

if __name__ == '__main__':
    import unittest
    unittest.main()
