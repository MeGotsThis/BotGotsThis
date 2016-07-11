from datetime import timedelta
from functools import partial, wraps
from typing import Any, Callable, Iterable, Optional, Tuple, Union
from ... import data

_AnyArgs = Union[data.ChatCommandArgs, data.WhisperCommandArgs]
_AnyCallable = Callable[..., Any]
_AnyDecorator = Callable[..., _AnyCallable]


def send(chat: Any) -> data.Send:
    return chat.send


def sendPriority(chat: Any,
                 priority: int) -> data.Send:
    return partial(chat.send, priority=priority)


def permission(level: str) -> _AnyDecorator:
    def decorator(func: _AnyCallable) -> _AnyCallable:
        @wraps(func)
        def command(args: _AnyArgs,
                    *pargs, **kwargs) -> Any:
            if not args.permissions[level]:
                return False
            return func(args, *pargs, **kwargs)
        return command
    return decorator


def not_permission(level: str) -> _AnyDecorator:
    def decorator(func: _AnyCallable) -> _AnyCallable:
        @wraps(func)
        def command(args: _AnyArgs,
                    *pargs, **kwargs) -> Any:
            if args.permissions[level]:
                return False
            return func(args, *pargs, **kwargs)
        return command
    return decorator


def ownerChannel(func: _AnyCallable) -> _AnyCallable:
    @wraps(func)
    def chatCommand(args: data.ChatCommandArgs,
                    *pargs, **kwargs) -> Any:
        if not args.permissions.inOwnerChannel:
            return False
        return func(args, *pargs, **kwargs)
    return chatCommand


def feature(featureKey: str):
    def decorator(func: _AnyCallable) -> _AnyCallable:
        @wraps(func)
        def chatCommand(args: data.ChatCommandArgs,
                        *pargs, **kwargs) -> Any:
            if not args.database.hasFeature(args.chat.channel, featureKey):
                return False
            return func(args, *pargs, **kwargs)
        return chatCommand
    return decorator


def not_feature(featureKey: str):
    def decorator(func: _AnyCallable) -> _AnyCallable:
        @wraps(func)
        def chatCommand(args: data.ChatCommandArgs,
                        *pargs, **kwargs) -> Any:
            if args.database.hasFeature(args.chat.channel, featureKey):
                return False
            return func(args, *pargs, **kwargs)
        return chatCommand
    return decorator


def permission_feature(*levelFeatures: Tuple[str, str]):
    def decorator(func: _AnyCallable) -> _AnyCallable:
        @wraps(func)
        def chatCommand(args: data.ChatCommandArgs,
                        *pargs, **kwargs) -> Any:
            for level, featureKey in levelFeatures:  # --type: str, str
                hasPermission = level is None or args.permissions[level]
                hasFeature = (featureKey is None
                              or args.database.hasFeature(args.chat.channel,
                                                          featureKey))
                if hasPermission and hasFeature:
                    break
            else:
                return False
            return func(args, *pargs, **kwargs)
        return chatCommand
    return decorator


def permission_not_feature(*levelFeatures: Tuple[str, str]):
    def decorator(func: _AnyCallable) -> _AnyCallable:
        @wraps(func)
        def chatCommand(args: data.ChatCommandArgs,
                        *pargs, **kwargs) -> Any:
            for level, featureKey in levelFeatures:  # --type: str, str
                hasPermission = level is None or args.permissions[level]
                hasFeature = (featureKey is None
                              or not args.database.hasFeature(
                                  args.chat.channel, featureKey))
                if hasPermission and hasFeature:
                    break
            else:
                return False
            return func(args, *pargs, **kwargs)
        return chatCommand
    return decorator


def cooldown(duration: timedelta,
             key: Any,
             level: Optional[str]=None):
    def decorator(func: _AnyCallable) -> _AnyCallable:
        @wraps(func)
        def chatCommand(args: data.ChatCommandArgs,
                        *pargs, **kwargs) -> Any:
            if inCooldown(args, duration, key, level):
                return False
            return func(args, *pargs, **kwargs)
        return chatCommand
    return decorator


def inCooldown(args: data.ChatCommandArgs,
               duration: timedelta,
               key: Any,
               level: Optional[str]=None):
    if ((level is None or not args.permissions[level])
            and key in args.chat.sessionData
            and args.timestamp - args.chat.sessionData[key] < duration):
        return True
    args.chat.sessionData[key] = args.timestamp
    return False


def min_args(amount: int,
             _return: bool=False,
             reason: Optional[str]=None):
    def decorator(func: _AnyCallable) -> _AnyCallable:
        @wraps(func)
        def command(args: data.ChatCommandArgs,
                    *pargs, **kwargs) -> Any:
            if len(args.message) < amount:
                if reason:
                    args.chat.send(reason)
                return _return
            return func(args, *pargs, **kwargs)
        return command
    return decorator
