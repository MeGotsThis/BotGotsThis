from bot import utils
from functools import partial, wraps
from typing import Any, Callable, Optional, cast
from . import chat
from ... import data

_AnyCallable = Callable[..., Any]
_AnyDecorator = Callable[..., _AnyCallable]


def send(nick: Any) -> data.Send:
    return cast(data.Send, partial(utils.whisper, nick))


permission = chat.permission
not_permission = chat.not_permission


def min_args(amount: int,
             _return: bool=False,
             reason: Optional[str]=None) -> _AnyDecorator:
    def decorator(func: _AnyCallable) -> _AnyCallable:
        @wraps(func)
        async def command(args: data.WhisperCommandArgs,
                          *pargs: Any, **kwargs: Any) -> bool:
            if len(args.message) < amount:
                if reason:
                    utils.whisper(args.nick, reason)
                return _return
            return await func(args, *pargs, **kwargs)
        return command
    return decorator
