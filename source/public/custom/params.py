import re

def fieldParams(field, param, default, message, msgParts, channel, nick,
                query):
    try:
        match = re.fullmatch(r'(\d+)(-(\d+))?|(\d+)-|-(\d+)', field)
        if match is not None:
            matchParts = match.groups()
            if matchParts[0] is not None:
                i = int(matchParts[0])
                if i >= len(msgParts):
                    return default
                if matchParts[2] is None:
                    return msgParts[i]
                else:
                    s = message.split(None, i)[i]
                    j = int(matchParts[2])
                    if len(msgParts) > j:
                        k = len(msgParts) - j - 1
                        return s.rsplit(None, k)[0]
                    else:
                        return s
            elif matchParts[3] is not None:
                i = int(matchParts[3])
                msgParts = message.split(None, i)
                if i < len(msgParts):
                    return msgParts[i]
                else:
                    return default
            elif matchParts[4] is not None:
                i = int(matchParts[4])
                if i == 0:
                    return msgParts[0]
                elif len(msgParts) >= 2:
                    if len(msgParts) <= i:
                        return message.split(None, 1)[1]
                    else:
                        k = len(msgParts) - i - 1
                        msg = message.rsplit(None, k)[0]
                        return msg.split(None, 1)[1]
                else:
                    return default
    except TypeError:
        return None
