from bot import globals, utils
from contextlib import suppress
from collections import defaultdict
from datetime import datetime, timedelta
from functools import wraps
from http.client import HTTPException
from typing import Any, Callable, Sequence, Tuple

_AnyCallable = Callable[..., Any]
_AnyDecorator = Callable[..., _AnyCallable]
_ArgsKey = Tuple[Tuple[Any, ...], Tuple[Tuple[str, Any], ...]]

def cache(key: str,
          duration: timedelta=timedelta(seconds=60), *,
          excepts: Sequence[BaseException]=(ConnectionError, HTTPException),
          default: Any=None) -> _AnyDecorator:
    def decorator(func: _AnyCallable) -> _AnyCallable:
        if key not in globals.globalSessionData:
            _ = defaultdict(lambda: (datetime.min, default))  # type: defaultdict
            globals.globalSessionData[key] = _

        @wraps(func)
        def data(*args, **kwargs) -> Any:
            kargs = args, tuple(kwargs.items())  # type: _ArgsKey
            lastTime, value = globals.globalSessionData[key][kargs]  # type: datetime, Any
            if utils.now() - lastTime >= duration:
                with suppress(excepts):
                    value = func(*args, **kwargs)
                    globals.globalSessionData[key][kargs] = utils.now(), value
            return value
        return data
    return decorator
