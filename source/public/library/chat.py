from functools import wraps

def send(chat):
    return chat.sendMessage

def permission(permission):
    def decorator(func):
        @wraps(func)
        def command(args):
            if not args.permissions[permission]:
                return False
            return func(args)
        return command
    return decorator

def not_permission(permission):
    def decorator(func):
        @wraps(func)
        def command(args):
            if not args.permissions[permission]:
                return False
            return func(args)
        return command
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

def permission_feature(*permissionFeatures):
    def decorator(func):
        @wraps(func)
        def chatCommand(args):
            for permission, feature in permissionFeatures:
                hasPermission = not permission or args.permissions[permission]
                hasFeature = (not feature
                              or args.database.hasFeature(args.chat.channel,
                                                          feature))
                if hasPermission and hasFeature:
                    break
            else:
                return False
            return func(args)
        return chatCommand
    return decorator

def permission_not_feature(*permissionFeatures):
    def decorator(func):
        @wraps(func)
        def chatCommand(args):
            for permission, feature in permissionFeatures:
                hasPermission = not permission or args.permissions[permission]
                hasFeature = (not feature
                              or not args.database.hasFeature(
                                  args.chat.channel, feature))
                if hasPermission and hasFeature:
                    break
            else:
                return False
            return func(args)
        return chatCommand
    return decorator

def cooldown(duration, key, permission=None):
    def decorator(func):
        @wraps(func)
        def chatCommand(args):
            if inCooldown(args, duration, key, permission):
                return False
            return func(args)
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
        def command(args):
            if len(args.message) < amount:
                if message:
                    args.chat.send(reason)
                return _return
            return func(args)
        return command
    return decorator
