from datetime import timedelta
from functools import wraps
from typing import Any, Callable, Iterable, Optional, Tuple, Union
from ... import data

_AnyArgs = Union[data.ChatCommandArgs, data.WhisperCommandArgs]
_AnyCallable = Callable[..., Any]
_AnyDecorator = Callable[..., _AnyCallable]


def send(chat: Any) -> data.Send:
    return chat.send


def sendPriority(chat: Any,
                 priority: int) -> data.Send:
    def sendMessages(messages: Union[str, Iterable[str]]):
        return chat.send(messages, priority)
    return sendMessages


def permission(permission: str) -> _AnyDecorator:
    def decorator(func: _AnyCallable) -> _AnyCallable:
        @wraps(func)
        def command(args: _AnyArgs,
                    *pargs, **kwargs) -> Any:
            if not args.permissions[permission]:
                return False
            return func(args, *pargs, **kwargs)
        return command
    return decorator


def not_permission(permission: str) -> _AnyDecorator:
    def decorator(func: _AnyCallable) -> _AnyCallable:
        @wraps(func)
        def command(args: _AnyArgs,
                    *pargs, **kwargs) -> Any:
            if not args.permissions[permission]:
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


def feature(feature: str):
    def decorator(func: _AnyCallable) -> _AnyCallable:
        @wraps(func)
        def chatCommand(args: data.ChatCommandArgs,
                        *pargs, **kwargs) -> Any:
            if not args.database.hasFeature(args.chat.channel, feature):
                return False
            return func(args, *pargs, **kwargs)
        return chatCommand
    return decorator


def not_feature(feature: str):
    def decorator(func: _AnyCallable) -> _AnyCallable:
        @wraps(func)
        def chatCommand(args: data.ChatCommandArgs,
                        *pargs, **kwargs) -> Any:
            if args.database.hasFeature(args.chat.channel, feature):
                return False
            return func(args, *pargs, **kwargs)
        return chatCommand
    return decorator


def permission_feature(*permissionFeatures: Tuple[str, str]):
    def decorator(func: _AnyCallable) -> _AnyCallable:
        @wraps(func)
        def chatCommand(args: data.ChatCommandArgs,
                        *pargs, **kwargs) -> Any:
            for permission, feature in permissionFeatures:  # --type: str, str
                hasPermission = not permission or args.permissions[permission]
                hasFeature = (not feature
                              or args.database.hasFeature(args.chat.channel,
                                                          feature))
                if hasPermission and hasFeature:
                    break
            else:
                return False
            return func(args, *pargs, **kwargs)
        return chatCommand
    return decorator


def permission_not_feature(*permissionFeatures: Tuple[str, str]):
    def decorator(func: _AnyCallable) -> _AnyCallable:
        @wraps(func)
        def chatCommand(args: data.ChatCommandArgs,
                        *pargs, **kwargs) -> Any:
            for permission, feature in permissionFeatures:  # --type: str, str
                hasPermission = not permission or args.permissions[permission]
                hasFeature = (not feature
                              or not args.database.hasFeature(
                                  args.chat.channel, feature))
                if hasPermission and hasFeature:
                    break
            else:
                return False
            return func(args, *pargs, **kwargs)
        return chatCommand
    return decorator


def cooldown(duration: timedelta,
             key: Any,
             permission: Optional[str]=None):
    def decorator(func: _AnyCallable) -> _AnyCallable:
        @wraps(func)
        def chatCommand(args: data.ChatCommandArgs,
                        *pargs, **kwargs) -> Any:
            if inCooldown(args, duration, key, permission):
                return False
            return func(args, *pargs, **kwargs)
        return chatCommand
    return decorator


def inCooldown(args: data.ChatCommandArgs,
               duration: timedelta,
               key: Any,
               permission: Optional[str]=None):
    if ((permission is None or not args.permissions[permission])
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
