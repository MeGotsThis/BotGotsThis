import lists.custom
from typing import Dict, Iterable, List, Optional
from ...data import ChatCommandArgs, CustomFieldArgs, CustomCommand
from ...data import CommandActionTokens, CustomCommandProcess
from ...data import CustomFieldParts, CustomProcessArgs
from ...data.message import Message
from ...data.permissions import ChatPermissionSet
from ...database import DatabaseBase
from ..library import textformat


permissions = {
    None: '',
    '': '',
    'any': '',
    'all': '',
    'public': '',
    'permitted': 'permitted',
    'permit': 'permitted',
    'subscriber': 'subscriber',
    'sub': 'subscriber',
    'moderator': 'moderator',
    'mod': 'moderator',
    'broadcaster': 'broadcaster',
    'streamer': 'broadcaster',
    'me': 'broadcaster',
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


def get_command(database: DatabaseBase,
                command: str,
                channel: str,
                permissions: ChatPermissionSet) -> Optional[CustomCommand]:
    commands = database.getChatCommands(channel, command)  # type: Dict[str, Dict[str, str]]
    permissionsSet = ['', 'subscriber', 'moderator', 'broadcaster',
                      'globalMod', 'admin', 'staff', 'owner']  # type: List[str]
    for permission in reversed(permissionsSet):  # type: str
        if not permission or permissions[permission]:
            for broadcaster in [channel, '#global']:  # type: str
                if permission in commands[broadcaster]:
                    message = commands[broadcaster][permission]  # type: str
                    return CustomCommand(message, broadcaster, permission)
    return None


def create_messages(command: CustomCommand,
                    args: ChatCommandArgs) -> List[str]:
    textFormat = args.database.hasFeature(args.chat.channel, 'textconvert')
    messageParts = []  # type: List[str]
    try:
        for parts in split_message(command.message):  # type: CustomFieldParts
            messageParts.append(parts.plainText)
            try:
                if parts.field is not None:
                    fieldArgument = CustomFieldArgs(
                        parts.field, parts.param, parts.prefix,
                        parts.suffix, parts.default, args.message,
                        args.chat.channel, args.nick, args.permissions,
                        args.timestamp)  # type: CustomFieldArgs
                    string = convert_field(fieldArgument)  # type: Optional[str]
                    if string is not None:
                        string = format(string, parts.format, textFormat)
                    else:
                        string = parts.original
                    messageParts.append(string)
            except Exception:
                messageParts.append(parts.original)
    except ValueError:
        return [str(command.message)]
    messages = [''.join(messageParts)]  # type: List[str]
    processArgument = CustomProcessArgs(
        args.database, args.chat, args.tags, args.nick, args.permissions,
        command.broadcaster, command.level, args.message.command,
        messages)  # type: CustomProcessArgs
    for process in lists.custom.postProcess:  # type: CustomCommandProcess
        process(processArgument)
    return messages


def parse_action_message(message: Message, broadcaster: str) -> Optional[CommandActionTokens]:
    try:
        action = message.lower[1]
        i = 2
        level = None  # type: Optional[str]
        if message[2].startswith('level='):
            i = 3
            level = message.lower[2][len('level='):]
        if level in permissions:
            level = permissions[level]
        else:
            level = None
        command = message[i]
        text = message[i+1:]
        
        return CommandActionTokens(action, broadcaster, level, command, text)
    except:
        return None


def split_message(message: str) -> Iterable[CustomFieldParts]:
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
                parsed.append(
                    CustomFieldParts(''.join(noFormat), None, None, None, None,
                                     None, None, None))
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

        format = None  # type: Optional[List[str]]
        if char == ':':
            format = []
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

        prefix = None  # type: Optional[List[str]]
        if char == '<':
            prefix = []
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

        suffix = None  # type: Optional[List[str]]
        if char == '>':
            suffix = []
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

        param = None  # type: Optional[List[str]]
        if char == '@':
            param = []
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

        default = None  # type: Optional[List[str]]
        if char == '!':
            default = []
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
            CustomFieldParts(
                ''.join(noFormat),
                ''.join(field),
                ''.join(format) if format is not None else None,
                ''.join(prefix) if prefix is not None else None,
                ''.join(suffix) if suffix is not None else None,
                ''.join(param) if param is not None else None,
                ''.join(default) if default is not None else None,
                original))
        
    return parsed


def convert_field(args: CustomFieldArgs) -> Optional[str]:
    for convert in lists.custom.fields:  # type: CustomCommandField
        result = convert(args)  # type: Optional[str]
        if result is not None:
            return result
    return None


def format(string: str,
           format: Optional[str],
           hasTextConvert: bool) -> str:
    if hasTextConvert and format is not None:
        return textformat.format(string=string, format_=format)
    return string
