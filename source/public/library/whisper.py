from functools import wraps

def permission(permission):
    def decorator(func):
        @wraps(func)
        def chatCommand(args):
            if not args.permissions[permission]:
                return False
            return func(args)
        return chatCommand
    return decorator
