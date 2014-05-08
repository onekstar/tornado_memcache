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

class TimeoutError(Exception):
    pass

class ConnectionTimeoutError(TimeoutError):
    pass

class Client:
    'client'
    
    def __init__(self, hosts, logger=logging, io_loop=None, connection_timeout=1):
        
        self.hosts = hosts
        self.dead_hosts = hosts
        self.io_loop = io_loop or tornado.ioloop.IOLoop.instance()
        self.connection_map = {}
        self.logger = logger
        self.connection_timeout = connection_timeout
    
    def get(self, key):
        
        pass
    
    def set(self, key, value, expire):
        
        pass
    
    def send_cmd(self, cmd, host):
        
        pass
    
    def parse_response(self, response):
        
        pass

    @tornado.gen.coroutine
    def connect(self, host):
        'connect to host'

        _timeout_handle = self.add_timeout(self.connection_timeout, error=ConnectionTimeoutError)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        stream = tornado.iostream.IOStream(s)
        _host, _port = host.split(':', 1)
        yield tornado.gen.Task(stream.connect, (_host, int(_port)))
        self.remove_timeout(_timeout_handle)
        self.connection_map[host] = stream
        raise tornado.gen.Return(1)
    
    def close(self):
        'close all streams'
        
        for stream in self.connection_map.values():
            stream.close()
    
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
