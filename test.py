#coding:utf-8
from tornado.testing import AsyncTestCase, gen_test
from tornado_memcache import Client, ConnectionTimeoutError
import tornado.ioloop

class BaseTestCase(AsyncTestCase):
    'Base Test Case'

    def get_new_ioloop(self):
        
        return tornado.ioloop.IOLoop.instance()

class ClientTestCase(BaseTestCase):
    'Client Test Case'

    @gen_test
    def test_connect(self):
        '测试正常连接'
        
        host = '127.0.0.1:11211'
        client = Client([host])
        yield client.connect(host)
        self.assertIn(host, client.connection_map)
 
    @gen_test
    def test_connect_when_no_socket(self):
        '测试连接不存在的服务'
        
        host = '127.0.0.1:45445'
        client = Client([host], connection_timeout=0.1)
        try:
            yield client.connect(host)
            self.assertTrue(False)
        except ConnectionTimeoutError:
            self.assertTrue(True)

if __name__ == '__main__':

    import unittest
    unittest.main()
