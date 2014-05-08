#coding:utf-8
from tornado.testing import AsyncTestCase, gen_test
from tornado_memcache import Client, ConnectionTimeoutError, WriteTimeoutError
import tornado.ioloop
import tornado.iostream
import socket
import uuid

class BaseTestCase(AsyncTestCase):
    'Base Test Case'

    def get_new_ioloop(self):
        
        return tornado.ioloop.IOLoop.instance()

class ClientTestCase(BaseTestCase):
    'Client Test Case'

    @gen_test
    def test_connect(self):
        'test normal connection'
        
        host = '127.0.0.1:11211'
        client = Client([host])
        stream = yield client.connect(host)
        self.assertFalse(stream._connecting)
        self.assertFalse(stream._closed)
 
    @gen_test
    def test_connect_when_no_socket(self):
        'test connect when socket server do not exists'
        
        host = '127.0.0.1:45445'
        client = Client([host], connection_timeout=0.1)
        try:
            yield client.connect(host)
            self.assertTrue(False)
        except ConnectionTimeoutError:
            self.assertTrue(True)
    
    @gen_test
    def test_write_to_stream_when_no_socket(self):
        'test write to stream when no socket'
    
        client = Client([], write_timeout=0.1)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        stream = tornado.iostream.IOStream(s)
        stream.connect(('127.0.0.1', 45445))
        try:
            yield client.write_to_stream(stream, 'abc')
            self.assertTrue(False)
        except WriteTimeoutError:
            self.assertTrue(True)
    
    def test_get_host(self):
        'test get host'
        
        hosts = ['127.0.0.1:11211', '127.0.0.1:11212']
        client = Client(hosts)
        client.get_host('1')
        client.get_host('2')
    
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
