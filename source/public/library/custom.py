import lists.custom
from typing import Dict, Iterable, List, Optional
from ...data import ChatCommandArgs, CustomFieldArgs, CustomCommand
from ...data import CommandActionTokens, CustomCommandField
from ...data import CustomCommandProcess, CustomFieldParts, CustomProcessArgs
from ...data.message import Message
from ...data.permissions import ChatPermissionSet
from ...database import DatabaseMain
from ..library import textformat


permissions: Dict[Optional[str], str] = {
    None: '',
    '': '',
    'any': '',
    'all': '',
    'public': '',
    'regular': '',
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
    'manager': 'manager',
    'botmanager': 'manager',
    'owner': 'owner',
    'self': 'owner',
    'bot': 'owner',
    }

permissionsOrder: List[str] = [
    '', 'permitted', 'subscriber', 'moderator', 'broadcaster', 'globalMod',
    'admin', 'staff', 'manager', 'owner']


def get_command(database: DatabaseMain,
                command: str,
                channel: str,
                permissions: ChatPermissionSet) -> Optional[CustomCommand]:
    commands: Dict[str, Dict[str, str]]
    commands = database.getChatCommands(channel, command)
    permission: str
    broadcaster: str
    message: str
    for permission in reversed(permissionsOrder):
        if not permission or permissions[permission]:
            for broadcaster in [channel, '#global']:
                if permission in commands[broadcaster]:
                    message = commands[broadcaster][permission]
                    return CustomCommand(message, broadcaster, permission)
    return None


async def create_messages(command: CustomCommand,
                    args: ChatCommandArgs) -> List[str]:
    textFormat = args.database.hasFeature(args.chat.channel, 'textconvert')
    messageParts: List[str] = []
    try:
        parts: CustomFieldParts
        for parts in split_message(command.message):
            messageParts.append(parts.plainText)
            try:
                if parts.field is not None:
                    fieldArgument: CustomFieldArgs = CustomFieldArgs(
                        parts.field, parts.param, parts.prefix,
                        parts.suffix, parts.default, args.message,
                        args.chat.channel, args.nick, args.permissions,
                        args.timestamp)
                    string: Optional[str] = await convert_field(fieldArgument)
                    if string is not None:
                        string = format(string, parts.format, textFormat)
                    else:
                        string = parts.original
                    messageParts.append(string)
            except Exception:
                messageParts.append(parts.original)
    except ValueError:
        return [str(command.message)]
    messages: List[str] = [''.join(messageParts)]
    processArgument: CustomProcessArgs = CustomProcessArgs(
        args.database, args.chat, args.tags, args.nick, args.permissions,
        command.broadcaster, command.level, args.message.command,
        messages)
    process: CustomCommandProcess
    for process in lists.custom.postProcess:
        await process(processArgument)
    return messages


def parse_action_message(message: Message,
                         broadcaster: str) -> Optional[CommandActionTokens]:
    try:
        action = message.lower[1]
        i = 2
        level: Optional[str] = None
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
    parsed: List[CustomFieldParts] = []
    i: int = 0
    length: int = len(message)
    
    while True:
        noFormat: List[str] = []
        while i < length:
            char: str = message[i]
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
        
        s: int = i
        i += 1
        if i == length:
            raise ValueError()
        
        field: List[str] = []
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

        format: Optional[List[str]] = None
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

        prefix: Optional[List[str]] = None
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

        suffix: Optional[List[str]] = None
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

        param: Optional[List[str]] = None
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

        default: Optional[List[str]] = None
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
        original: str = message[s:i]
        
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


async def convert_field(args: CustomFieldArgs) -> Optional[str]:
    convert: CustomCommandField
    for convert in lists.custom.fields:
        result: Optional[str] = await convert(args)
        if result is not None:
            return result
    return None


def format(string: str,
           format: Optional[str],
           hasTextConvert: bool) -> str:
    if hasTextConvert and format is not None:
        return textformat.format(string=string, format_=format)
    return string
