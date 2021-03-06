import bot.data  # noqa: F401

from collections import defaultdict
from datetime import datetime, timedelta
from functools import partial, wraps
from typing import Any, Awaitable, Callable, Optional, Tuple, Union, cast

from lib import data

_AnyArgs = Union[data.ChatCommandArgs, data.WhisperCommandArgs,
                 data.ManageBotArgs]
_AnyCallable = Callable[..., Awaitable[bool]]
_AnyDecorator = Callable[..., _AnyCallable]


def send(chat: 'bot.data.Channel') -> data.Send:
    return chat.send


def sendPriority(chat: 'bot.data.Channel',
                 priority: int) -> data.Send:
    return cast(data.Send, partial(chat.send, priority=priority))


def permission(level: str) -> _AnyDecorator:
    def decorator(func: _AnyCallable) -> _AnyCallable:
        @wraps(func)
        async def command(args: _AnyArgs,
                          *pargs: Any, **kwargs: Any) -> bool:
            if not args.permissions[level]:
                return False
            return await func(args, *pargs, **kwargs)
        return command
    return decorator


def not_permission(level: str) -> _AnyDecorator:
    def decorator(func: _AnyCallable) -> _AnyCallable:
        @wraps(func)
        async def command(args: _AnyArgs,
                          *pargs: Any, **kwargs: Any) -> bool:
            if args.permissions[level]:
                return False
            return await func(args, *pargs, **kwargs)
        return command
    return decorator


def ownerChannel(func: _AnyCallable) -> _AnyCallable:
    @wraps(func)
    async def chatCommand(args: data.ChatCommandArgs,
                          *pargs: Any, **kwargs: Any) -> bool:
        if not args.permissions.inOwnerChannel:
            return False
        return await func(args, *pargs, **kwargs)
    return chatCommand


def feature(featureKey: str) -> _AnyDecorator:
    def decorator(func: _AnyCallable) -> _AnyCallable:
        @wraps(func)
        async def chatCommand(args: data.ChatCommandArgs,
                              *pargs: Any, **kwargs: Any) -> bool:
            hasFeature: bool = await args.data.hasFeature(
                args.chat.channel, featureKey)
            if not hasFeature:
                return False
            return await func(args, *pargs, **kwargs)
        return chatCommand
    return decorator


def not_feature(featureKey: str) -> _AnyDecorator:
    def decorator(func: _AnyCallable) -> _AnyCallable:
        @wraps(func)
        async def chatCommand(args: data.ChatCommandArgs,
                              *pargs: Any, **kwargs: Any) -> bool:
            hasFeature: bool = await args.data.hasFeature(
                args.chat.channel, featureKey)
            if hasFeature:
                return False
            return await func(args, *pargs, **kwargs)
        return chatCommand
    return decorator


def permission_feature(*levelFeatures: Tuple[str, str]) -> _AnyDecorator:
    def decorator(func: _AnyCallable) -> _AnyCallable:
        @wraps(func)
        async def chatCommand(args: data.ChatCommandArgs,
                              *pargs: Any, **kwargs: Any) -> bool:
            level: str
            featureKey: str
            for level, featureKey in levelFeatures:
                hasPermission: bool = level is None or args.permissions[level]
                hasFeature: bool = (featureKey is None
                                    or await args.data.hasFeature(
                                        args.chat.channel, featureKey))
                if hasPermission and hasFeature:
                    break
            else:
                return False
            return await func(args, *pargs, **kwargs)
        return chatCommand
    return decorator


def permission_not_feature(*levelFeatures: Tuple[str, str]) -> _AnyDecorator:
    def decorator(func: _AnyCallable) -> _AnyCallable:
        @wraps(func)
        async def chatCommand(args: data.ChatCommandArgs,
                              *pargs: Any, **kwargs: Any) -> bool:
            level: str
            featureKey: str
            for level, featureKey in levelFeatures:
                hasPermission: bool = level is None or args.permissions[level]
                hasFeature: bool = (featureKey is None
                                    or not await args.data.hasFeature(
                                        args.chat.channel, featureKey))
                if hasPermission and hasFeature:
                    break
            else:
                return False
            return await func(args, *pargs, **kwargs)
        return chatCommand
    return decorator


def cooldown(duration: timedelta,
             key: Any,
             level: Optional[str]=None) -> _AnyDecorator:
    def decorator(func: _AnyCallable) -> _AnyCallable:
        @wraps(func)
        async def chatCommand(args: data.ChatCommandArgs,
                              *pargs: Any, **kwargs: Any) -> bool:
            if inCooldown(args, duration, key, level):
                return False
            return await func(args, *pargs, **kwargs)
        return chatCommand
    return decorator


def inCooldown(args: data.ChatCommandArgs,
               duration: timedelta,
               key: Any,
               level: Optional[str]=None) -> bool:
    if ((level is None or not args.permissions[level])
            and key in args.chat.sessionData
            and args.timestamp - args.chat.sessionData[key] < duration):
        return True
    args.chat.sessionData[key] = args.timestamp
    return False


def in_user_cooldown(args: data.ChatCommandArgs,
                     cooldown: timedelta,
                     key: Any,
                     level: Optional[str]=None) -> bool:
    if key not in args.chat.sessionData:
        args.chat.sessionData[key] = defaultdict(lambda: datetime.min)
    if level is None or not args.permissions[level]:
        since: timedelta
        since = args.timestamp - args.chat.sessionData[key][args.nick]
        if since < cooldown:
            return True
    args.chat.sessionData[key][args.nick] = args.timestamp
    return False


def min_args(amount: int,
             _return: bool=False,
             reason: Optional[str]=None) -> _AnyDecorator:
    def decorator(func: _AnyCallable) -> _AnyCallable:
        @wraps(func)
        async def command(args: data.ChatCommandArgs,
                          *pargs: Any, **kwargs: Any) -> bool:
            if len(args.message) < amount:
                if reason:
                    args.chat.send(reason)
                return _return
            return await func(args, *pargs, **kwargs)
        return command
    return decorator
