from collections import OrderedDict

from typing import Any, Dict, Callable, Optional, Tuple, TypeVar, TYPE_CHECKING

_KT = TypeVar('_KT')
_VT = TypeVar('_VT')

if TYPE_CHECKING:
    OD = OrderedDict[_KT, _VT]
else:
    OD = OrderedDict


class DefaultOrderedDict(OD, Dict[_KT, _VT]):
    # Source: http://stackoverflow.com/a/6190500/562769
    def __init__(self,
                 default_factory: Optional[Callable[[], _VT]]=None,
                 *args: Any,
                 **kwargs: Any) -> None:
        if default_factory is not None:
            if not callable(default_factory):
                raise TypeError('first argument must be callable')
        OrderedDict.__init__(self, *args, **kwargs)
        self.default_factory: Optional[Callable[[], _VT]] = default_factory

    def __getitem__(self, key: _KT) -> _VT:
        try:
            return OrderedDict.__getitem__(self, key)
        except KeyError:
            return self.__missing__(key)

    def __missing__(self, key: _KT) -> _VT:
        if self.default_factory is None:
            raise KeyError(key)
        value: _VT
        self[key] = value = self.default_factory()
        return value

    def __reduce__(self) -> Tuple[Any, ...]:
        args:  Tuple[Any, ...]
        if self.default_factory is None:
            args = tuple()
        else:
            args = self.default_factory,
        return type(self), args, None, None, self.items()

    def copy(self) -> 'DefaultOrderedDict[_KT, _VT]':
        return self.__copy__()

    def __copy__(self) -> 'DefaultOrderedDict[_KT, _VT]':
        return type(self)(self.default_factory, self)

    def __deepcopy__(self, memo: Any) -> 'DefaultOrderedDict[_KT, _VT]':
        import copy
        return type(self)(self.default_factory,
                          copy.deepcopy(self.items()))

    def __repr__(self) -> str:
        return 'OrderedDefaultDict(%s, %s)' % (self.default_factory,
                                               OrderedDict.__repr__(self))
