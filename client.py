#coding:utf-8
import tornado.gen
from binascii import crc32
import tornado.ioloop
import logging
from connection import Connection


def cmemcache_hash(key):
    
    return((((crc32(key) & 0xffffffff) >> 16) & 0x7fff) or 1)

server_hash_function = cmemcache_hash

_FLAG_INTEGER = 1<<1
_FLAG_LONG    = 1<<2

class Client:
    'client'
    
    def __init__(self, hosts, logger=logging, io_loop=None, connection_timeout=1, read_timeout=2, write_timeout=1):
        
        self.hosts = hosts
        self.dead_hosts = hosts
        self.io_loop = io_loop or tornado.ioloop.IOLoop.instance()
        self.logger = logger
        self.connection_timeout = connection_timeout
        self.read_timeout = read_timeout
        self.write_timeout = write_timeout
    
    @tornado.gen.coroutine
    def get(self, key):
        'Execute get CMD'
        
        connection = self.get_connection(key=key)
        cmd = '%s %s' %('get', key)
        yield connection.send_cmd(cmd)
        head = yield connection.read_one_line()
        if head == 'END':
            connection.close()
            raise tornado.gen.Return(None)
        length = int(head.split(' ')[-1])
        response = yield connection.read_bytes(length)
        connection.close()
        raise tornado.gen.Return(response)

    @tornado.gen.coroutine
    def set(self, key, value, expire):
        'Execute set CMD'
        
        flags, value = self.get_store_info(value)
        connection = self.get_connection(key=key)
        cmd = "%s %s %d %d %d\r\n%s" %('set', key, flags, expire, len(value), value) 
        yield connection.send_cmd(cmd)
        response = yield connection.read_one_line()
        connection.close()
        raise tornado.gen.Return(response == 'STORED')
    
    def get_store_info(self, value):
        'Transform val to a storable representation, returning a tuple of the flags, and the new value itself.'
        
        flags = 0
        if isinstance(value, str):
            pass
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        elif isinstance(value, int):
            flags |= _FLAG_INTEGER
            value = "%d" % value 
        elif isinstance(value, long):
            flags |= _FLAG_LONG
            value = "%d" % value 
        return (flags, value)
    
    @tornado.gen.coroutine
    def incr(self, key, delta=1):
        'Execute incr CMD'

        result = yield self._incr_or_decr('incr', key, delta)
        raise tornado.gen.Return(result)

    @tornado.gen.coroutine
    def decr(self, key, delta=1):
        'Execute incr CMD'

        result = yield self._incr_or_decr('decr', key, delta)
        raise tornado.gen.Return(result)
    
    @tornado.gen.coroutine
    def delete(self, key):
        'Execute delete CMD'

        connection = self.get_connection(key=key)
        cmd = 'delete %s' %(key) 
        yield connection.send_cmd(cmd)
        response = yield connection.read_one_line()
        connection.close()
        raise tornado.gen.Return(response in ('DELETED', 'NOT_FOUND'))

    @tornado.gen.coroutine
    def _incr_or_decr(self, cmd, key, delta):
        'Execute incr CMD'

        connection = self.get_connection(key=key)
        cmd = '%s %s %d' %(cmd, key, delta) 
        yield connection.send_cmd(cmd)
        response = yield connection.read_one_line()
        if not response.isdigit():
            connection.close()
            raise tornado.gen.Return(None)
        connection.close()
        raise tornado.gen.Return(int(response))
    
    def get_host(self, key):
        'get host for a key'

        key_hash = server_hash_function(key)
        return self.hosts[key_hash % len(self.hosts)]
    
    def get_connection(self, key=None, host=None):
        'get connection instance by key or specific host'
        
        if host is None: 
            host = self.get_host(key)
        return Connection(host, io_loop=self.io_loop, connection_timeout=self.connection_timeout, 
            read_timeout=self.read_timeout, write_timeout=self.write_timeout)  
