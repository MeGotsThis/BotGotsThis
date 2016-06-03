from bot import utils
from functools import partial, wraps

def send(nick):
    return functools.partial(utils.whisper, nick)

def permission(permission):
    def decorator(func):
        @wraps(func)
        def whisperCommand(args):
            if not args.permissions[permission]:
                return False
            return func(args)
        return whisperCommand
    return decorator

def min_args(amount, _return=False, reason=None):
    def decorator(func):
        @wraps(func)
        def whisperCommand(args):
            if len(args.message) < amount:
                if message:
                    args.chat.send(reason)
                return _return
            return func(args)
        return whisperCommand
    return decorator
