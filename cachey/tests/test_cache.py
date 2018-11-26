import sys
from time import sleep

from cachey import Cache, Scorer, nbytes


def test_cache():
    c = Cache(available_bytes=nbytes(1) * 3)

    c.put('x', 1, 10)
    assert c.get('x') == 1
    assert 'x' in c

    c.put('a', 1, 10)
    c.put('b', 1, 10)
    c.put('c', 1, 10)
    assert set(c.data) == set('xbc')
    c.put('d', 1, 10)
    assert set(c.data) == set('xcd')

    c.clear()
    assert 'x' not in c
    assert not c.data
    assert not c.heap

def test_cache_resize():
    c = Cache(available_bytes=nbytes(1) * 3)

    c.put('x', 1, 10)
    assert c.get('x') == 1
    assert 'x' in c

    c.put('a', 1, 10)
    c.put('b', 1, 10)
    c.put('c', 1, 10)
    assert set(c.data) == set('xbc')
    c.put('d', 1, 10)
    assert set(c.data) == set('xcd')

    # resize will shrink
    c.resize(available_bytes=nbytes(1) * 1)

    assert set(c.data) == set('x')

    c.resize(available_bytes=nbytes(1) * 10)

    assert set(c.data) == set('x')

def test_cache_scores_update():
    c = Cache(available_bytes=nbytes(1) * 2)
    c.put('x', 1, 1)
    c.put('y', 1, 1)
    c.get('x')
    c.get('x')
    c.get('x')

    c.put('z', 1, 1)
    assert set(c.data) == set('xz')


def test_memoize():
    c = Cache(available_bytes=nbytes(1) * 3)

    flag = [0]
    def slow_inc(x):
        flag[0] += 1
        sleep(0.01)
        return x + 1

    memo_inc = c.memoize(slow_inc)

    assert memo_inc(1) == 2
    assert memo_inc(1) == 2

    assert list(c.data.values()) == [2]


def test_callbacks():
    hit_flag = [False]
    def hit(key, value):
        hit_flag[0] = (key, value)

    miss_flag = [False]
    def miss(key):
        miss_flag[0] = key

    c = Cache(100, hit=hit, miss=miss)

    c.get('x')
    assert miss_flag[0] == 'x'
    assert hit_flag[0] == False

    c.put('y', 1, 1)
    c.get('y')
    assert hit_flag[0] == ('y', 1)


def test_just_one_reference():
    c = Cache(available_bytes=1000)
    o = object()
    x = sys.getrefcount(o)

    c.put('key', o, cost=10)
    y = sys.getrefcount(o)
    assert y == x + 1

    c.retire('key')
    z = sys.getrefcount(o)
    assert z == x
