from collections import OrderedDict

from typing import Any, Callable, Optional, Tuple, TypeVar

_KT = TypeVar('_KT')
_VT = TypeVar('_VT')


class DefaultOrderedDict(OrderedDict[_KT, _VT]):
    # Source: http://stackoverflow.com/a/6190500/562769
    def __init__(self,
                 default_factory: Optional[Callable[[], _VT]]=None,
                 *args: Any,
                 **kwargs: Any) -> None: ...

    def __getitem__(self, key: _KT) -> _VT: ...

    def __missing__(self, key: _KT) -> _VT:
        ...

    def __reduce__(self) -> Tuple[Any, ...]: ...

    def copy(self) -> DefaultOrderedDict[_KT, _VT]: ...

    def __copy__(self) -> DefaultOrderedDict[_KT, _VT]: ...

    def __deepcopy__(self, memo: Any) -> DefaultOrderedDict[_KT, _VT]: ...

    def __repr__(self) -> str: ...
