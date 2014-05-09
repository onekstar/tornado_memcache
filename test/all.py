#coding:utf-8
import unittest
from test_client import ClientTestCase
from test_connection import ConnectionTestCase

tests = [
    ClientTestCase,
    ConnectionTestCase,
]

if __name__ == '__main__':
    suite = unittest.TestSuite()
    for test in tests:
        suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(test))
    unittest.TextTestRunner().run(suite)
