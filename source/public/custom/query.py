def fieldQuery(args):
    if args.field.lower() == 'query':
        if len(args.message) > 1:
            return args.prefix + args.message.query + args.suffix
        else:
            return args.default
    return None
