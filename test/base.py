#coding:utf-8
from tornado.testing import AsyncTestCase
import tornado.ioloop

class BaseTestCase(AsyncTestCase):
    'Base Test Case'

    def get_new_ioloop(self):
        
        return tornado.ioloop.IOLoop.instance()
