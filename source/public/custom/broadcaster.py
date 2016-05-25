def fieldBroadcaster(args):
    if args.field.lower() == 'broadcaster' or args.field.lower() == 'streamer':
        if args.channel:
            return args.prefix + args.channel + args.suffix
        else:
            return args.default
    return None
