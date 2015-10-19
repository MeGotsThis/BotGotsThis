def fieldQuery(field, param, default, message, msgParts, channel, nick, query):
    if field.lower() == 'query':
        return query if query else default
    return None
