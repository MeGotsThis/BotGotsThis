﻿def fieldUser(field, param, prefix, suffix, default, message,
              channel, nick, now):
    if field.lower() == 'user' or field.lower() == 'nick':
        return prefix + nick + suffix if nick else default
    return None
