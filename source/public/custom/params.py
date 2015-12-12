import re

def fieldParams(field, param, prefix, suffix, default, message,
                msgParts, channel, nick, query, now):
    try:
        match = re.fullmatch(r'(\d+)(-(\d+))?|(\d+)-|-(\d+)', field)
        if match is not None:
            matchParts = match.groups()
            if matchParts[0] is not None:
                i = int(matchParts[0])
                if i >= len(msgParts):
                    return default
                if matchParts[2] is None:
                    return prefix + msgParts[i] + suffix
                else:
                    s = message.split(None, i)[i]
                    j = int(matchParts[2])
                    if len(msgParts) > j:
                        k = len(msgParts) - j - 1
                        return prefix + s.rsplit(None, k)[0] + suffix
                    else:
                        return prefix + s + suffix
            elif matchParts[3] is not None:
                i = int(matchParts[3])
                msgParts = message.split(None, i)
                if i < len(msgParts):
                    return prefix + msgParts[i] + suffix
                else:
                    return default
            elif matchParts[4] is not None:
                i = int(matchParts[4])
                if i == 0:
                    return prefix + msgParts[0] + suffix
                elif len(msgParts) >= 2:
                    if len(msgParts) <= i:
                        return prefix + message.split(None, 1)[1] + suffix
                    else:
                        k = len(msgParts) - i - 1
                        msg = message.rsplit(None, k)[0]
                        return prefix + msg.split(None, 1)[1] + suffix
                else:
                    return default
    except TypeError:
        pass
    return None
