#coding:utf-8
import uuid
from base import BaseTestCase
from tornado.testing import gen_test
from client import Client

class ClientTestCase(BaseTestCase):

    @gen_test
    def test_set(self):
        'test set cache'

        key = uuid.uuid4().hex
        client = Client(['127.0.0.1:11211'])
        res = yield client.set(key, 'value', 5)
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

if __name__ == '__main__':
    import unittest
    unittest.main()
