#coding:utf-8
import tornado.gen
from binascii import crc32
import tornado.ioloop
import logging
from connection import Connection


def cmemcache_hash(key):
    
    return((((crc32(key) & 0xffffffff) >> 16) & 0x7fff) or 1)

server_hash_function = cmemcache_hash

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
        'Execute GET CMD'
        
        connection = self.get_connection(key)
        cmd = '%s %s' %('get', key)
        yield connection.send_cmd(cmd)
        head = yield connection.read_one_line()
        if head == 'END':
            raise tornado.gen.Return(None)
        length = int(head.split(' ')[-1])
        response = yield connection.read_bytes(length)
        raise tornado.gen.Return(response)

    @tornado.gen.coroutine
    def set(self, key, value, expire):
        'Execute SET CMD'
        
        connection = self.get_connection(key)
        cmd = "%s %s %d %d %d\r\n%s" %('set', key, 0, expire, len(value), value) 
        stream = yield connection.send_cmd(cmd)
        response = yield connection.read_one_line()
        raise tornado.gen.Return(response == 'STORED')
    
    def get_host(self, key):
        'get host for a key'

        key_hash = server_hash_function(key)
        return self.hosts[key_hash % len(self.hosts)]
    
    def get_connection(self, key):
        'get connection instance'
        
        host = self.get_host(key)
        return Connection(host, io_loop=self.io_loop, connection_timeout=self.connection_timeout, 
            read_timeout=self.read_timeout, write_timeout=self.write_timeout)  
        
