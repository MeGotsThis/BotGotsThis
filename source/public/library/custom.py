from ...data.argument import CustomFieldArgs, CustomProcessArgs
from ...data.return_ import CustomCommand, CustomCommandTokens
from ...data.return_ import CustomFieldParts
from ..library import textformat
import lists.custom


def getCustomCommand(database, command, channel, permissions):
    commands = database.getChatCommands(channel, command)
    permissionsSet = ['', 'turbo', 'subscriber', 'moderator', 'broadcaster',
                      'globalMod', 'admin', 'staff', 'owner']
    for permission in reversed(permissionsSet):
        if not permission or permissions[permission]:
            for broadcaster in [channel, '#global']:
                if permission in commands[channel]:
                    message = commands[broadcaster][permission]
                    return CustomCommand(message, broadcaster, permission)
    return None


def createMessages(command, args):
    textFormat = args.database.hasFeature(args.chat.channel, 'textconvert')
    messageParts = []
    try:
        for formats in parseFormatMessage(command.message):
            messageParts.append(formats.plainText)
            try:
                if formats.field is not None:
                    fieldArgument = CustomFieldArgs(
                        formats.field, formats.param, formats.prefix,
                        formats.suffix, formats.default, args.message,
                        args.chat.channel, args.nick, args.timestamp)
                    string = fieldString(fieldArgument)
                    if string is not None:
                        string = format(string, formats.format, textFormat)
                    else:
                        string = formats.original
                    messageParts.append(string)
            except Exception:
                messageParts.append(formats.original)
    except Exception:
        messageParts = [str(command.message)]
    messages = [''.join(messageParts)]
    processArgument = CustomProcessArgs(
        args.database, args.chat, args.tags, args.nick, args.permissions,
        command.broadcaster, command.level, args.message.command, messages)
    for process in lists.custom.postProcess:
        process(processArgument)
    return messages


def parseCommandMessageInput(message, broadcaster):
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
        text = message[i+1:]
        
        return CustomCommandTokens(action, broadcaster, level, command, text)
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
