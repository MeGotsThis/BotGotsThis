from bot import utils
from functools import partial, wraps
from typing import Any, Callable, Optional, Union
from . import chat
from ...data import argument

_AnyCallable = Callable[..., Any]
_AnyDecorator = Callable[..., _AnyCallable]


def send(nick: Any) -> argument.Send:
    return partial(utils.whisper, nick)  # type: ignore

permission = chat.permission
not_permission = chat.not_permission


def min_args(amount: int,
             _return: bool=False,
             reason: Optional[str]=None):
    def decorator(func: _AnyCallable) -> _AnyCallable:
        @wraps(func)
        def command(args: argument.WhisperCommandArgs,
                    *pargs, **kwargs) -> Any:
            if len(args.message) < amount:
                if reason:
                    utils.whisper(args.nick, reason)
                return _return
            return func(args, *pargs, **kwargs)
        return command
    return decorator
