def fieldUser(args):
    if args.field.lower() == 'user' or args.field.lower() == 'args.nick':
        if args.nick:
            return args.prefix + args.nick + args.suffix
        else:
            return args.default
    return None
