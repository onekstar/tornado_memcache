tornado_memcache
==============

async memcache client on python and tornado


Installation
------------

You should user tornado 3.1+

You can just use the source code in tornado_memcache

Usage
-----
Normally, you can find the usage in the test package.

```python
import tornado.gen
from tornado_memcache.client import Client

...

client = Client(['127.0.0.1:11211'])

...
@tornado.gen.coroutine
def get(self):
    result = yield client.set('k', 'v', 5)
    value = yield client.get('k')
```

Exception
-----
1. The functions may throw exception. For example, ConnectionTimeoutError, ReadTimeoutError.So please handle the exception when use it.

