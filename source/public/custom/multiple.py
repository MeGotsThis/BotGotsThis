def propertyMultipleLines(args):
    if not args.database.getCustomCommandProperty(
            args.broadcaster, args.level, args.command, 'multiple'):
        return
    
    delimiter = args.database.getCustomCommandProperty(
        args.broadcaster, args.level, args.command, 'delimiter') or '&&'
    
    msgs = args.messages[:]
    args.messages.clear()
    for msg in msgs:
        args.messages.extend(msg.split(delimiter))
