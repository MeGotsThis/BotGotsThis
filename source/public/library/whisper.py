from bot import utils
from functools import partial, wraps
from typing import Any, Callable, Optional, Union
from . import chat
from ... import data

_AnyCallable = Callable[..., Any]
_AnyDecorator = Callable[..., _AnyCallable]


def send(nick: Any) -> data.Send:
    # TODO: mypy/typeshed fix
    return partial(utils.whisper, nick)  # type: ignore

permission = chat.permission
not_permission = chat.not_permission


def min_args(amount: int,
             _return: bool=False,
             reason: Optional[str]=None):
    def decorator(func: _AnyCallable) -> _AnyCallable:
        @wraps(func)
        async def command(args: data.WhisperCommandArgs,
                    *pargs, **kwargs) -> Any:
            if len(args.message) < amount:
                if reason:
                    utils.whisper(args.nick, reason)
                return _return
            return await func(args, *pargs, **kwargs)
        return command
    return decorator
