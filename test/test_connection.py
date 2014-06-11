#coding:utf-8
from tornado_memcache.connection import Connection, ConnectionTimeoutError, ReadTimeoutError, WriteTimeoutError
from base import BaseTestCase
from tornado.testing import gen_test

class ConnectionTestCase(BaseTestCase):
 
    @gen_test
    def test_connect_when_no_socket(self):
        'test connect when socket server do not exists'
        
        host = '127.0.0.1:45445'
        conn = Connection(host, connection_timeout=0.1)
        try:
            yield conn.connect()
            self.assertTrue(False)
        except ConnectionTimeoutError:
            self.assertTrue(True)

    @gen_test
    def test_connect(self):
        'test normal connection'
        
        host = '127.0.0.1:11211'
        conn = Connection(host)
        stream = yield conn.connect()
        self.assertFalse(conn.stream._connecting)
        self.assertFalse(conn.stream._closed)
    
    @gen_test
    def test_send_cmd(self):
        'test send cmd'

        host = '127.0.0.1:11211'
        conn = Connection(host)
        yield conn.send_cmd('delete abc')

    @gen_test
    def test_read_one_line(self):
        'test read one line'

        host = '127.0.0.1:11211'
        conn = Connection(host)
        yield conn.send_cmd('delete abc')
        response = yield conn.read_one_line()
        self.assertTrue(response)

    @gen_test
    def test_read_bytes(self):
        'test read bytes'

        host = '127.0.0.1:11211'
        conn = Connection(host)
        yield conn.send_cmd('delete abc')
        response = yield conn.read_bytes(2)
        self.assertTrue(response)

if __name__ == '__main__':
    
    import unittest
    unittest.main()
