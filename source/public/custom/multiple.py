def propertyMultipleLines(db, chat, tags, nick, permissions, broadcaster,
                          level, command, messages):
    if not db.getCustomCommandProperty(broadcaster, level, command,
                                       'multiple'):
        return
    
    delimiter = db.getCustomCommandProperty(
        broadcaster, level, command, 'delimiter') or '&&'
    
    msgs = messages[:]
    messages.clear()
    for msg in msgs:
        messages.extend(msg.split(delimiter))
