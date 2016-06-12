from typing import Dict, Iterable, List, Optional
from ...data import ChatCommandArgs, CustomFieldArgs, CustomCommand
from ...data import CustomCommandTokens, CustomCommandProcess
from ...data import CustomFieldParts, CustomProcessArgs
from ...data.message import Message
from ...data.permissions import ChatPermissionSet
from ...database import DatabaseBase
from ..library import textformat
import lists.custom


def getCustomCommand(database: DatabaseBase,
                     command: str,
                     channel: str,
                     permissions: ChatPermissionSet) -> Optional[CustomCommand]:
    commands = database.getChatCommands(channel, command)  # type: Dict[str, Dict[str, str]]
    permissionsSet = ['', 'turbo', 'subscriber', 'moderator', 'broadcaster',
                      'globalMod', 'admin', 'staff', 'owner']  # type: List[str]
    for permission in reversed(permissionsSet):  # --type: str
        if not permission or permissions[permission]:
            for broadcaster in [channel, '#global']:  # --type: str
                if permission in commands[channel]:
                    message = commands[broadcaster][permission]  # --type: str
                    return CustomCommand(message, broadcaster, permission)
    return None


def createMessages(command: CustomCommand,
                   args: ChatCommandArgs) -> List[str]:
    textFormat = args.database.hasFeature(args.chat.channel, 'textconvert')
    messageParts = []  # type: List[str]
    try:
        for formats in parseFormatMessage(command.message):
            messageParts.append(formats.plainText)
            try:
                if formats.field is not None:
                    fieldArgument = CustomFieldArgs(
                        formats.field, formats.param, formats.prefix,
                        formats.suffix, formats.default, args.message,
                        args.chat.channel, args.nick, args.timestamp)  # type: CustomFieldArgs
                    string = fieldString(fieldArgument)  # type: Optional[str]
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
        command.broadcaster, command.level, args.message.command, messages)  # type: CustomProcessArgs
    for process in lists.custom.postProcess:  # --type: CustomCommandProcess
        process(processArgument)
    return messages


def parseCommandMessageInput(message: Message,
                             broadcaster: str) -> Optional[CustomCommandTokens]:
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
        level = None  # type: Optional[str]
        if message[2].startswith('level='):
            i = 3
            level = message[2][len('level='):]
        if level in allowPermissions:
            level = allowPermissions[level]
        else:
            level = None
        command = message[i]
        text = message[i+1:]
        
        return CustomCommandTokens(action, broadcaster, level, command, text)
    except:
        return None


def parseFormatMessage(message:str) -> Iterable[CustomFieldParts]:
    # Format: {field:format<prefix>suffix@param!default}
    parsed = []  # type: List[CustomFieldParts]
    i = 0  # type: int
    length = len(message)  # type: int
    
    while True:
        noFormat = []  # type: List[str]
        while i < length:
            char = message[i]  # type: str
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
                parsed.append(CustomFieldParts(''.join(noFormat), None, None, None, None, None, None, None))
            break
        
        s = i  # type: int
        i += 1
        if i == length:
            raise ValueError()
        
        field = []  # type: List[str]
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

        format = []  # type: List[str]
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

        prefix = []  # type: List[str]
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

        suffix = []  # type: List[str]
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

        param = []  # type: List[str]
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

        default = []  # type: List[str]
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


def fieldString(args: CustomFieldArgs) -> Optional[str]:
    for fieldConvert in lists.custom.fields:  # --type: CustomCommandField
        result = fieldConvert(args)  # type: Optional[str]
        if result is not None:
            return result
    return None


def format(string: str,
           format: str,
           hasTextConvert: bool) -> str:
    if hasTextConvert:
        return textformat.format(string=string, format=format)
    return string
