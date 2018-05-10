Caching for Analytic Computations
---------------------------------

Humans repeat stuff.  Caching helps.

Normal caching policies like LRU aren't well suited for analytic computations
where both the cost of recomputation and the cost of storage routinely vary by
one million or more.  Consider the following computations

```python
# Want this
np.std(x)        # tiny result, costly to recompute

# Don't want this
np.transpose(x)  # huge result, cheap to recompute
```

Cachey tries to hold on to values that have the following characteristics

1. Expensive to recompute (in seconds)
2. Cheap to store (in bytes)
3. Frequently used
4. Recenty used

It accomplishes this by adding the following to each items score on each access

    score += compute_time / num_bytes * (1 + eps) ** tick_time

For some small value of epsilon (which determines the memory halflife.) This
has units of inverse bandwidth, has exponential decay of old results and
roughly linear amplification of repeated results.

Example
-------

```python
>>> from cachey import Cache
>>> c = Cache(1e9, 1)  # 1 GB, cut off anything with cost 1 or less

>>> c.put('x', 'some value', cost=3)
>>> c.put('y', 'other value', cost=2)

>>> c.get('x')
'some value'
```

This also has a `memoize` method

```python
>>> memo_f = c.memoize(f)
```

Status
------

Cachey is new and not robust.
