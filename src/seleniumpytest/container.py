from .wrapper import SeleniumWrapper
from .wrapper import _chainreact
from .wrapper import _is_wrappable
import collections

class SeleniumContainerWrapper(object):

    def __init__(self, iterable):
        if not isinstance(iterable, collections.Sequence):
            msg = "2nd argument should be an instance of collections.Sequence. given %s".format(type(iterable))
            raise TypeError(msg)
        self._iterable = iterable

    @classmethod
    def wrap(cls, iterable):
        try:
            return SeleniumContainerWrapper(iterable)
        except TypeError, e:
            raise e

    @_chainreact
    def __getattr__(self, name):
        """Wrap return value using '_chanreact'."""
        return self._iterable, getattr(self._iterable, name)

    def __getitem__(self, key):
        obj = self._iterable[key]
        if _is_wrappable(obj):
            return SeleniumWrapper(obj)
        return obj

    def __len__(self):
        return len(self._iterable)

    def __contains__(self, key):
        return key in self._iterable
