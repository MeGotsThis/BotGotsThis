from contextlib import suppress
import re

def fieldParams(field, param, prefix, suffix, default, message,
                channel, nick, now):
    with suppress(TypeError):
        match = re.fullmatch(r'(\d+)(-(\d+))?|(\d+)-|-(\d+)', field)
        if match is not None:
            matchParts = match.groups()
            start = None
            stop = None
            if matchParts[0] is not None:
                start = int(matchParts[0])
                if matchParts[2] is not None:
                    stop = int(matchParts[2])
                else:
                    if start < len(message):
                        return prefix + message[start] + suffix
                    else:
                        return default
            elif matchParts[3] is not None:
                start = int(matchParts[3])
            elif matchParts[4] is not None:
                stop = int(matchParts[4])
            params = message[start:stop]
            if params:
                return prefix + params + suffix
            else:
                return default
    return None
