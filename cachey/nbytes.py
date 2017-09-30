import sys


def _array(x):
    if x.dtype == 'O':
        return sys.getsizeof('0'*100) * x.size
    elif str(x.dtype) == 'category':
        return _array(x.codes) + _array(x.categories)
    else:
        return x.nbytes


def nbytes(o):
    """ Number of bytes of an object

    >>> nbytes(123)  # doctest: +SKIP
    24

    >>> nbytes('Hello, world!')  # doctest: +SKIP
    50

    >>> import numpy as np
    >>> nbytes(np.ones(1000, dtype='i4'))
    4000
    """
    name = type(o).__module__ + '.' + type(o).__name__

    if name == 'pandas.core.series.Series':
        return _array(o._data.blocks[0].values) + _array(o.index._data)
    elif name == 'pandas.core.frame.DataFrame':
        return _array(o.index) + sum([_array(blk.values)
                                     for blk in o._data.blocks])
    elif name == 'numpy.ndarray':
        return _array(o)
    elif hasattr(o, 'nbytes'):
        return o.nbytes
    elif isinstance(o, (list, tuple)):
        return sum(nbytes(x) for x in o)    
    else:
        return sys.getsizeof(o)
