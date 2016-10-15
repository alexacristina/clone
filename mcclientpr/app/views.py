from django.shortcuts import render
from django.core.cache import cache
from clonememcache import mymemcached
from django.http import HttpResponse

def fibonacci(n):
    "Return the nth fibonacci number."
    if n in (0, 1):
        return n
    return fibonacci(n-1) + fibonacci(n-2)


def heavy_view(request):
    cache_key = 'my_heavy_view_cache_key'
    new_key = 'my_other_heavy_view_cache_key'
    cache_time = 180
    mymemcached.set(key=cache_key, body="This is a messed up cache backend", time=cache_time)
    obj1 = mymemcached.get(cache_key)
    mymemcached.add(cache_key, "Not so loyal clone of cache", cache_time)
    obj2 = mymemcached.get(cache_key)
    if obj1 == obj2:
        mymemcached.add(new_key, "Not so loyal clone of cache", cache_time)
        obj2 = mymemcached.get(new_key)
    mymemcached.delete(cache_key)
    mymemcached.replace(new_key, fibonacci(16), cache_key)
    obj3 = mymemcached.get(new_key)
    return HttpResponse('%s %s %s' % (obj1, obj2, str(obj3)))

#