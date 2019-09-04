__all__ = [
    "lazy"
]


class lazy(tuple):
    """ Decorator for a method. Remembers the method output in the instance.
Then reuses the output so the method is called once.
    """

    def __new__(cls, getter):
        ret = tuple.__new__(cls, (getter,))
        return ret

    def __get__(self, obj, _type = None):
        getter = self[0]
        val = getter(obj)
        obj.__dict__[getter.__name__] = val
        return val
