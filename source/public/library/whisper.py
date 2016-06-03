from bot import utils
from functools import partial, wraps

def send(nick):
    return functools.partial(utils.whisper, nick)

def permission(permission):
    def decorator(func):
        @wraps(func)
        def chatCommand(args):
            if not args.permissions[permission]:
                return False
            return func(args)
        return chatCommand
    return decorator
