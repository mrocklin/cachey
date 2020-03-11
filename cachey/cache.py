from .nbytes import nbytes
from .score import Scorer
from heapdict import heapdict
import time

def cost(nbytes, time):
    return float(time) / nbytes / 1e9


def memo_key(args, kwargs):
    result = (args, frozenset(list(kwargs.items())))
    try:
        hash(result)
    except TypeError:
        result = tuple(map(id, args)), str(kwargs)
    return result


class Cache(object):
    """ A cache that prefers long-running cheap-to-store computations

    This cache prefers computations that have the following properties:

    1.  Costly to compute (seconds)
    2.  Cheap to store (bytes)
    3.  Frequently used
    4.  Recently used

    Parameters
    ----------

    available_bytes: int
        The number of bytes of data to keep in the cache
    limit: float
        The minimum cost something must be to consider to keep in the cache
    scorer: optional with halflife
        A Scorer object (see cachey/scorer.py)
    halflife: int, optional with scorer
        The halflife in number of touches of the score of a piece of data
    nbytes: function (defaults to cachey/nbytes.py)
        Function to compute the number of bytes of an input.
    cost:  function  (defaults to cost())
        Determine cost from nbytes and time

    Example
    -------
    >>> from cachey import Cache
    >>> c = Cache(1e9, 10)  # 1GB of space, costs must be 10 or higher

    >>> c.put('x', 1, cost=50)
    >>> c.get('x')
    1

    >>> def inc(x):
    ...     return x + 1

    >>> memo_inc = c.memoize(inc)  # Memoize functions
    """
    def __init__(self, available_bytes, limit=0, scorer=None, halflife=1000,
                 nbytes=nbytes, cost=cost, hit=None, miss=None):
        if scorer is None:
            scorer = Scorer(halflife)
        self.scorer = scorer
        self.available_bytes = available_bytes
        self.limit = limit
        self.get_nbytes = nbytes
        self.cost = cost
        self.hit = hit
        self.miss = miss

        self.data = dict()
        self.heap = heapdict()
        self.nbytes = dict()
        self.total_bytes = 0

    def put(self, key, value, cost, nbytes=None):
        """ Put key-value data into cache with associated cost

        >>> c = Cache(1e9, 10)
        >>> c.put('x', 10, cost=50)
        >>> c.get('x')
        10
        """
        if nbytes is None:
            nbytes = self.get_nbytes(value)
        if cost >= self.limit and nbytes < self.available_bytes:
            score = self.scorer.touch(key, cost)
            if (nbytes + self.total_bytes < self.available_bytes or
                not self.heap or score > self.heap.peekitem()[1]):
                self.data[key] = value
                self.heap[key] = score
                self.nbytes[key] = nbytes
                self.total_bytes += nbytes
                self.shrink()

    def get(self, key, default=None):
        """ Get value associated with key.  Returns None if not present

        >>> c = Cache(1e9, 10)
        >>> c.put('x', 10, cost=50)
        >>> c.get('x')
        10
        """
        score = self.scorer.touch(key)
        if key in self.data:
            value = self.data[key]
            if self.hit is not None:
                self.hit(key, value)
            self.heap[key] = score
            return value
        else:
            if self.miss is not None:
                self.miss(key)
            return default

    def retire(self, key):
        """ Retire/remove a key from the cache

        See Also:
            shrink
        """
        val = self.data.pop(key)
        self.total_bytes -= self.nbytes.pop(key)

    def _shrink_one(self):
        try:
            key, score = self.heap.popitem()
        except IndexError:
            return
        self.retire(key)
        
        
    def resize(self, available_bytes):
        """ Resize the cache. 
            
            Will fit the cache into available_bytes by calling `shrink()`.
        """
        self.available_bytes = available_bytes
        self.shrink()
        
    def shrink(self):
        """ Retire keys from the cache until we're under bytes budget

        See Also:
            retire
        """
        if self.total_bytes <= self.available_bytes:
            return

        while self.total_bytes > self.available_bytes:
            self._shrink_one()

    def __contains__(self, key):
        return key in self.data

    def clear(self):
        while self.data:
            self._shrink_one()

    def __bool__(self):
        return not not self.data

    def memoize(self, func, key=memo_key):
        """ Create a cached function

        >>> def inc(x):
        ...     return x + 1

        >>> c = Cache(1e9)

        >>> memo_inc = c.memoize(inc)
        >>> memo_inc(1)  # computes first time
        2
        >>> memo_inc(1)  # uses cached result (if computation has a high score)
        2
        """
        def cached_func(*args, **kwargs):
            k = (func, key(args, kwargs))

            result = self.get(k)
            if result is None:
                start = time.time()
                result = func(*args, **kwargs)
                end = time.time()

                nb = nbytes(result)

                self.put(k, result, cost(nb, end - start), nbytes=nb)
            return result
        return cached_func
