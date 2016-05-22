def fieldQuery(field, param, prefix, suffix, default, message,
               tokens, channel, nick, query, now):
    if field.lower() == 'query':
        return prefix + query + suffix if query else default
    return None
