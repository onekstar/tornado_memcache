#coding:utf-8
import tornado.iostream
import tornado.gen
from binascii import crc32
import tornado.ioloop
from tornado import stack_context
import time
import socket
from functools import partial
import logging

__author__ = 'Wang Yuan <yuanwang.bupt@gmail.com>'
__version__ = '1.0'

def cmemcache_hash(key):
    
    return((((crc32(key) & 0xffffffff) >> 16) & 0x7fff) or 1)

server_hash_function = cmemcache_hash

class TimeoutError(Exception):
    pass

class ConnectionTimeoutError(TimeoutError):
    pass

class ReadTimeoutError(TimeoutError):
    pass

class WriteTimeoutError(TimeoutError):
    pass

class Client:
    'client'
    
    def __init__(self, hosts, logger=logging, io_loop=None, connection_timeout=1, read_timeout=2, write_timeout=1):
        
        self.hosts = hosts
        self.dead_hosts = hosts
        self.io_loop = io_loop or tornado.ioloop.IOLoop.instance()
        self.logger = logger
        self.connection_timeout = connection_timeout
    
    @tornado.gen.coroutine
    def get(self, key):
        'Execute GET CMD'
        
        host = self.get_host(key)
        cmd = '%s %s' %('get', key)
        stream = yield self.execute_cmd(cmd, host)
        head = yield self.read_one_line(stream)
        if head == 'END':
            raise tornado.gen.Return(None)
        length = int(head.split(' ')[-1])
        response = yield self.read_bytes(stream, length)
        raise tornado.gen.Return(response)

    @tornado.gen.coroutine
    def set(self, key, value, expire):
        'Execute SET CMD'
        
        host = self.get_host(key)
        cmd = "%s %s %d %d %d\r\n%s" %('set', key, 0, expire, len(value), value) 
        stream = yield self.execute_cmd(cmd, host)
        response = yield self.read_one_line(stream)
        raise tornado.gen.Return(response == 'STORED')
    
    def get_host(self, key):
        'get host for a key'

        key_hash = server_hash_function(key)
        return self.hosts[key_hash % len(self.hosts)]

    @tornado.gen.coroutine
    def execute_cmd(self, cmd, host):
        'execute cmd and return stream'
        
        stream = yield self.connect(host)
        yield self.write_to_stream(stream, cmd) 
        raise tornado.gen.Return(stream)
 
    @tornado.gen.coroutine
    def write_to_stream(self, stream, cmd):
        'write cmd to stream'
        
        _timeout_handle = self.add_timeout(self.connection_timeout, error=WriteTimeoutError)
        yield tornado.gen.Task(stream.write, '%s\r\n' %cmd)
        self.remove_timeout(_timeout_handle)

    @tornado.gen.coroutine
    def read_one_line(self, stream):
        'read one line from stream'

        _timeout_handle = self.add_timeout(self.connection_timeout, error=ReadTimeoutError)
        response = yield tornado.gen.Task(stream.read_until, '\r\n')
        self.remove_timeout(_timeout_handle)
        raise tornado.gen.Return(response.strip('\r\n'))
    
    @tornado.gen.coroutine
    def read_bytes(self, stream, length):
        'read bytes for length'

        _timeout_handle = self.add_timeout(self.connection_timeout, error=ReadTimeoutError)
        response = yield tornado.gen.Task(stream.read_bytes, length)
        self.remove_timeout(_timeout_handle)
        raise tornado.gen.Return(response)

    @tornado.gen.coroutine
    def connect(self, host):
        'connect to host'

        _timeout_handle = self.add_timeout(self.connection_timeout, error=ConnectionTimeoutError)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        stream = tornado.iostream.IOStream(s)
        _host, _port = host.split(':', 1)
        yield tornado.gen.Task(stream.connect, (_host, int(_port)))
        self.remove_timeout(_timeout_handle)
        raise tornado.gen.Return(stream)
    
    def _on_timeout(self, error=TimeoutError):
        'timeout callback'
        
        raise error()
    
    def add_timeout(self, seconds, error=TimeoutError):
        'add new timeout handle'
        
        return self.io_loop.add_timeout(time.time() + seconds, partial(self._on_timeout, error=error))
    
    def remove_timeout(self, timeout_handle):
        'remote one timeout handle'
        
        if isinstance(timeout_handle, tornado.ioloop._Timeout):
            self.io_loop.remove_timeout(timeout_handle)
