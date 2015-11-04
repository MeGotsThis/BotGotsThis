def fieldQuery(field, param, prefix, suffix, default,
               message, msgParts, channel, nick, query):
    if field.lower() == 'query':
        return prefix + query + suffix if query else default
    return None
