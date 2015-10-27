def fieldUser(field, param, default, message, msgParts, channel, nick, query):
    if field.lower() == 'user' or field.lower() == 'nick':
        return nick if nick else default
    return None
