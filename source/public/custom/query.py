def fieldQuery(field, param, prefix, suffix, default, message,
               channel, nick, now):
    if field.lower() == 'query':
        return prefix + message.query + suffix if len(message) > 1 else default
    return None
