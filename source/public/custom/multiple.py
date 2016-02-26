def propertyMultipleLines(db, chat, tags, nick, permissions, level, command,
                          messages):
    if not db.getCustomCommandProperty(chat.channel, level, command,
                                       'multiple'):
        return
    
    delimiter = db.getCustomCommandProperty(
        chat.channel, level, command, 'delimiter') or '&&'
    
    msgs = messages[:]
    messages.clear()
    for msg in msgs:
        messages.extend(msg.split(delimiter))
