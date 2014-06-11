#coding:utf-8
import socket
import time
from functools import partial
import tornado.ioloop
import tornado.gen
import tornado.iostream

class TimeoutError(Exception):
    pass

class ConnectionTimeoutError(TimeoutError):
    pass

class ReadTimeoutError(TimeoutError):
    pass

class WriteTimeoutError(TimeoutError):
    pass

class Connection:
    'async socket connection'
    
    def __init__(self, host, io_loop=None, connection_timeout=1, read_timeout=2, write_timeout=1):
        
        self.host = host
        self.io_loop = io_loop or tornado.ioloop.IOLoop.current()
        self.connection_timeout = connection_timeout
        self.read_timeout = read_timeout
        self.write_timeout = write_timeout
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        self.stream = tornado.iostream.IOStream(self.sock)
        self.tcp_timeout = None

    @tornado.gen.coroutine
    def connect(self):
        'connect to host'

        _timeout_handle = self.add_timeout(self.connection_timeout, error=ConnectionTimeoutError)
        self.tcp_timeout = self.add_timeout(self.io_loop.time()+10, error=None) #use this time out to prevent unclosed tcp connection
        _host, _port = self.host.split(':', 1)
        yield tornado.gen.Task(self.stream.connect, (_host, int(_port)))
        self.remove_timeout(_timeout_handle)

    @tornado.gen.coroutine
    def send_cmd(self, cmd):
        'execute cmd and return stream'
        
        yield self.connect()
        yield self.write(cmd) 
        raise tornado.gen.Return()

    @tornado.gen.coroutine
    def write(self, cmd):
        'write cmd to stream'
        
        _timeout_handle = self.add_timeout(self.connection_timeout, error=WriteTimeoutError)
        yield tornado.gen.Task(self.stream.write, '%s\r\n' %cmd)
        self.remove_timeout(_timeout_handle)
    
    @tornado.gen.coroutine
    def read_one_line(self):
        'read one line from stream'

        _timeout_handle = self.add_timeout(self.connection_timeout, error=ReadTimeoutError)
        response = yield tornado.gen.Task(self.stream.read_until, '\r\n')
        self.remove_timeout(_timeout_handle)
        raise tornado.gen.Return(response.strip('\r\n'))
    
    @tornado.gen.coroutine
    def read_bytes(self, length):
        'read bytes for length'

        _timeout_handle = self.add_timeout(self.connection_timeout, error=ReadTimeoutError)
        response = yield tornado.gen.Task(self.stream.read_bytes, length)
        self.remove_timeout(_timeout_handle)
        raise tornado.gen.Return(response)

    def _on_timeout(self, error=TimeoutError):
        'timeout callback'
        
        self.close()
        if error is not None:
            raise error()

    def add_timeout(self, seconds, error=TimeoutError):
        'add new timeout handle'
        
        return self.io_loop.add_timeout(time.time() + seconds, partial(self._on_timeout, error=error))
    
    def remove_timeout(self, timeout_handle):
        'remote one timeout handle'
        
        if isinstance(timeout_handle, tornado.ioloop._Timeout):
            self.io_loop.remove_timeout(timeout_handle)
    
    def close(self):
        
        self.remove_timeout(self.tcp_timeout)
        self.stream.close()
