from ..library import textformat
from bot.data.return_ import CustomCommandTokens, CustomFieldParts
import lists.custom

def parseCommandMessageInput(message):
    allowPermissions = {
        None: '',
        '': '',
        'any': '',
        'all': '',
        'public': '',
        'turbo': 'turbo',
        'twitchturbo': 'turbo',
        'subscriber': 'subscriber',
        'sub': 'subscriber',
        'moderator': 'moderator',
        'mod': 'moderator',
        'broadcaster': 'broadcaster',
        'streamer': 'broadcaster',
        'me': 'broadcaster',
        'globalMod': 'globalMod',
        'globalmod': 'globalMod',
        'global_mod': 'globalMod',
        'gmod': 'globalMod',
        'admin': 'admin',
        'twitchadmin': 'admin',
        'staff': 'staff',
        'twitchstaff': 'staff',
        'owner': 'owner',
        'self': 'owner',
        'bot': 'owner',
        }
    
    try:
        action = message.lower[1]
        i = 2
        level = None
        if message[2].startswith('level='):
            i = 3
            level = message[2][len('level='):]
        if level in allowPermissions:
            level = allowPermissions[level]
        else:
            level = False
        command = message[i]
        fullText = message[i+1:]
        
        return CustomCommandTokens(message.command, action, level, command,
                                   fullText)
    except:
        return None

def parseFormatMessage(message):
    # Format: {field:format<prefix>suffix@param!default}
    parsed = []
    i = 0
    length = len(message)
    
    while True:
        noFormat = []
        while i < length:
            char = message[i]
            i += 1
            
            if char == '}':
                if i < length and message[i] == '}':
                    i += 1
                else:
                    raise ValueError()
            elif char == '{':
                if i < length and message[i] == '{':
                    i += 1
                else:
                    i -= 1
                    break
            
            noFormat.append(char)
        
        if i == length:
            if noFormat:
                parsed.append(CustomFieldParts(''.join(noFormat)))
            break
        
        s = i
        i += 1
        if i == length:
            raise ValueError()
        
        field = []
        while True:
            if i == length:
                raise ValueError()
            
            char = message[i]
            i += 1
            
            if char == ':':
                if i < length and message[i] == ':':
                    i += 1
                else:
                    break
            if char == '<':
                if i < length and message[i] == '<':
                    i += 1
                else:
                    break
            if char == '>':
                if i < length and message[i] == '>':
                    i += 1
                else:
                    break
            if char == '@':
                if i < length and message[i] == '@':
                    i += 1
                else:
                    break
            if char == '!':
                if i < length and message[i] == '!':
                    i += 1
                else:
                    break
            if char == '{':
                if i < length and message[i] == '{':
                    i += 1
                else:
                    raise ValueError()
            if char == '}':
                if i < length and message[i] == '}':
                    i += 1
                else:
                    i -= 1
                    break
            field.append(char)

        format = []
        if char == ':':
            while True:
                if i == length:
                    raise ValueError()
                
                char = message[i]
                i += 1
                
                if char == '@':
                    if i < length and message[i] == '@':
                        i += 1
                    else:
                        break
                if char == '<':
                    if i < length and message[i] == '<':
                        i += 1
                    else:
                        break
                if char == '>':
                    if i < length and message[i] == '>':
                        i += 1
                    else:
                        break
                if char == '!':
                    if i < length and message[i] == '!':
                        i += 1
                    else:
                        break
                if char == '{':
                    if i < length and message[i] == '{':
                        i += 1
                    else:
                        raise ValueError()
                if char == '}':
                    if i < length and message[i] == '}':
                        i += 1
                    else:
                        i -= 1
                        break
                format.append(char)

        prefix = []
        if char == '<':
            while True:
                if i == length:
                    raise ValueError()
                
                char = message[i]
                i += 1
                
                if char == '>':
                    if i < length and message[i] == '>':
                        i += 1
                    else:
                        break
                if char == '@':
                    if i < length and message[i] == '@':
                        i += 1
                    else:
                        break
                if char == '!':
                    if i < length and message[i] == '!':
                        i += 1
                    else:
                        break
                if char == '{':
                    if i < length and message[i] == '{':
                        i += 1
                    else:
                        raise ValueError()
                if char == '}':
                    if i < length and message[i] == '}':
                        i += 1
                    else:
                        i -= 1
                        break
                prefix.append(char)

        suffix = []
        if char == '>':
            while True:
                if i == length:
                    raise ValueError()
                
                char = message[i]
                i += 1
                
                if char == '@':
                    if i < length and message[i] == '@':
                        i += 1
                    else:
                        break
                if char == '!':
                    if i < length and message[i] == '!':
                        i += 1
                    else:
                        break
                if char == '{':
                    if i < length and message[i] == '{':
                        i += 1
                    else:
                        raise ValueError()
                if char == '}':
                    if i < length and message[i] == '}':
                        i += 1
                    else:
                        i -= 1
                        break
                suffix.append(char)

        param = []
        if char == '@':
            while True:
                if i == length:
                    raise ValueError()
                
                char = message[i]
                i += 1
                
                if char == '!':
                    if i < length and message[i] == '!':
                        i += 1
                    else:
                        break
                if char == '{':
                    if i < length and message[i] == '{':
                        i += 1
                    else:
                        raise ValueError()
                if char == '}':
                    if i < length and message[i] == '}':
                        i += 1
                    else:
                        i -= 1
                        break
                param.append(char)

        default = []
        if char == '!':
            while True:
                if i == length:
                    raise ValueError()
                
                char = message[i]
                i += 1
                
                if char == '{':
                    if i < length and message[i] == '{':
                        i += 1
                    else:
                        raise ValueError()
                if char == '}':
                    if i < length and message[i] == '}':
                        i += 1
                    else:
                        i -= 1
                        break
                default.append(char)

        if char != '}':
            raise ValueError()
        i += 1
        original = message[s:i]
        
        parsed.append(
            CustomFieldParts(''.join(noFormat),
                             ''.join(field),
                             ''.join(format),
                             ''.join(prefix),
                             ''.join(suffix),
                             ''.join(param),
                             ''.join(default),
                             original))
        
    return parsed

def fieldString(args):
    for fieldConvert in lists.custom.fields:
        result = fieldConvert(args)
        if result is not None:
            return result
    return None

def format(string, format, hasTextConvert):
    if hasTextConvert:
        return textformat.format(string=string, format=format)
    return string
