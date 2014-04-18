#coding:utf-8
import tornado.iostream
import tonrado.gen
from binascii import crc32   # zlib version is not cross-platform

__author__ == 'Wang Yuan <yuanwang.bupt@gmail.com>'
__version__ == '1.0'

def cmemcache_hash(key):
    
    return((((crc32(key) & 0xffffffff) >> 16) & 0x7fff) or 1)

class ConnectionError(Exception):
    pass

class SocketIOError(Exception):
    pass

class ConnectionTimeoutError(ConnectionError):
    pass

class ReadTimeoutError(SocketIOError):
    pass

class WriteTimeoutError(SocketIOError):
    pass

class Client:
    'clients'
    
    def __init__(self, hosts, connection_timeout=3):
        
        self.hosts = hosts
        self.connection_timeout = connection_timeout

    @tornado.gen.coroutine
    def get(self, timeout=1):
        'get value by key'

        pass

    @tornado.gen.coroutine
    def set(self, key, value, expire, timeout=1):
        'set value for key'

        pass

    @tornado.gen.coroutine
    def send_cmd(self, cmd, timeout=1):
        'send command'

        pass

    @tornado.gen.coroutine
    def read_result(self, timeout=1):
        'read result'

        pass

if __name__ == '__main__':
    pass
