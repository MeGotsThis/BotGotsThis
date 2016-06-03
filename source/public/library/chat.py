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

def not_permission(permission):
    def decorator(func):
        @wraps(func)
        def chatCommand(args):
            if not args.permissions[permission]:
                return False
            return func(args)
        return chatCommand
    return decorator

def ownerChannel(func):
    @wraps(func)
    def chatCommand(args):
        if not args.permissions.inOwnerChannel:
            return False
        return func(args)
    return chatCommand

def feature(feature):
    def decorator(func):
        @wraps(func)
        def chatCommand(args):
            if not args.database.hasFeature(args.chat.channel, feature):
                return False
            return func(args)
        return chatCommand
    return decorator

def not_feature(feature):
    def decorator(func):
        @wraps(func)
        def chatCommand(args):
            if args.database.hasFeature(args.chat.channel, feature):
                return False
            return func(args)
        return chatCommand
    return decorator
