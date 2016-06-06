from functools import wraps


def send(chat):
    return chat.send


def permission(permission):
    def decorator(func):
        @wraps(func)
        def command(args, *pargs, **kwargs):
            if not args.permissions[permission]:
                return False
            return func(args, *pargs, **kwargs)
        return command
    return decorator


def not_permission(permission):
    def decorator(func):
        @wraps(func)
        def command(args, *pargs, **kwargs):
            if not args.permissions[permission]:
                return False
            return func(args, *pargs, **kwargs)
        return command
    return decorator


def ownerChannel(func):
    @wraps(func)
    def chatCommand(args, *pargs, **kwargs):
        if not args.permissions.inOwnerChannel:
            return False
        return func(args, *pargs, **kwargs)
    return chatCommand


def feature(feature):
    def decorator(func):
        @wraps(func)
        def chatCommand(args, *pargs, **kwargs):
            if not args.database.hasFeature(args.chat.channel, feature):
                return False
            return func(args, *pargs, **kwargs)
        return chatCommand
    return decorator


def not_feature(feature):
    def decorator(func):
        @wraps(func)
        def chatCommand(args, *pargs, **kwargs):
            if args.database.hasFeature(args.chat.channel, feature):
                return False
            return func(args, *pargs, **kwargs)
        return chatCommand
    return decorator


def permission_feature(*permissionFeatures):
    def decorator(func):
        @wraps(func)
        def chatCommand(args, *pargs, **kwargs):
            for permission, feature in permissionFeatures:
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


def permission_not_feature(*permissionFeatures):
    def decorator(func):
        @wraps(func)
        def chatCommand(args, *pargs, **kwargs):
            for permission, feature in permissionFeatures:
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


def cooldown(duration, key, permission=None):
    def decorator(func):
        @wraps(func)
        def chatCommand(args, *pargs, **kwargs):
            if inCooldown(args, duration, key, permission):
                return False
            return func(args, *pargs, **kwargs)
        return chatCommand
    return decorator


def inCooldown(args, duration, key, permission=None):
    if ((permission is None or not args.permissions[permission])
            and key in args.chat.sessionData
            and args.timestamp - args.chat.sessionData[key] < duration):
        return True
    args.chat.sessionData[key] = args.timestamp
    return False


def min_args(amount, _return=False, reason=None):
    def decorator(func):
        @wraps(func)
        def command(args, *pargs, **kwargs):
            if len(args.message) < amount:
                if reason:
                    args.chat.send(reason)
                return _return
            return func(args, *pargs, **kwargs)
        return command
    return decorator
