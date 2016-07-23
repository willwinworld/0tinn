# -*- coding:utf-8 -*-
from werkzeug.contrib.cache import RedisCache


def cached(timeout=60, key_name=None):
    redis_cache = RedisCache(default_timeout=timeout)

    def real_wrap(f):
        def wrap_f(*args, **kwargs):
            if key_name is None:
                raise ValueError("key_name is None!")
            rv = redis_cache.get(key=key_name)
            if rv is None:
                rv = f(*args, **kwargs)
                redis_cache.set(key=key_name, value=rv, timeout=timeout)
            return rv
        return wrap_f
    return real_wrap


