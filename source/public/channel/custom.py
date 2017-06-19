import bot.config
import lists.custom
import textwrap
from bot import utils
from ..library import chat, custom, timeout
from ..library.chat import min_args, not_feature, permission, ownerChannel
from ...data import ChatCommandArgs, CustomCommand, CommandActionTokens
from datetime import timedelta
from typing import Awaitable, Callable, Dict, List, Optional


@not_feature('nocustom')
async def customCommands(args: ChatCommandArgs) -> bool:
    command: Optional[CustomCommand]
    command = await custom.get_command(args.database, args.message.command,
                                       args.chat.channel, args.permissions)
    if command is not None:
        cooldown: timedelta
        cooldown = timedelta(seconds=bot.config.customMessageCooldown)
        if chat.inCooldown(args, cooldown, 'customCommand', 'moderator'):
            return False

        cooldown = timedelta(seconds=bot.config.customMessageUserCooldown)
        if chat.in_user_cooldown(args, cooldown, 'customUserCommand',
                                 'moderator'):
            return False
        
        msgs: List[str] = await custom.create_messages(command, args)
        args.chat.send(msgs)
        if args.permissions.chatModerator:
            await timeout.record_timeout(args.chat, args.nick, msgs,
                                         str(args.message), 'custom')
        return True
    return False


@ownerChannel
@permission('admin')
async def commandGlobal(args: ChatCommandArgs) -> bool:
    return await process_command(args, '#global')


@not_feature('nocustom')
@permission('moderator')
async def commandCommand(args: ChatCommandArgs) -> bool:
    return await process_command(args, args.chat.channel)


@min_args(3)
async def process_command(args: ChatCommandArgs,
                          broadcaster: str) -> bool:
    input: Optional[CommandActionTokens] = custom.parse_action_message(
        args.message, broadcaster)
    if input is None:
        return False

    if input.level is None:
        args.chat.send(
            '{user} -> Invalid level, command ignored'.format(user=args.nick))
        return True
    if input.level:
        try:
            if not args.permissions[input.level]:
                args.chat.send('{user} -> You do not have permission to set '
                               'that level'.format(user=args.nick))
                return True
        except KeyError:
            args.chat.send('{user} -> Invalid level, command '
                           'ignored'.format(user=args.nick))
            return True

    actions: Dict[str, Callable[[ChatCommandArgs, CommandActionTokens],
                                Awaitable[bool]]]
    actions = {
        'add': insert_command,
        'insert': insert_command,
        'new': insert_command,
        'edit': update_command,
        'update': update_command,
        'replace': replace_command,
        'override': replace_command,
        'append': append_command,
        'del': delete_command,
        'delete': delete_command,
        'rem': delete_command,
        'remove': delete_command,
        'property': command_property,
        'raw': raw_command,
        'original': raw_command,
        'level': level_command,
        'rename': rename_command,
        }
    if input.action in actions:
        return await actions[input.action](args, input)
    else:
        return False


async def insert_command(args: ChatCommandArgs,
                   input: CommandActionTokens) -> bool:
    message: str
    successful: bool = await args.database.insertCustomCommand(
        input.broadcaster, input.level, input.command, input.text, args.nick)
    if successful:
        message = '{user} -> {command} was added successfully'
    else:
        message = ('{user} -> {command} was not added successfully. There '
                   'might be an existing command')
    args.chat.send(message.format(user=args.nick, command=input.command))
    return True


async def update_command(args: ChatCommandArgs,
                         input: CommandActionTokens) -> bool:
    message: str
    successful: bool = await args.database.updateCustomCommand(
        input.broadcaster, input.level, input.command, input.text, args.nick)
    if successful:
        message = '{user} -> {command} was updated successfully'
    else:
        message = ('{user} -> {command} was not updated successfully. The '
                   'command might not exist')
    args.chat.send(message.format(user=args.nick, command=input.command))
    return True


async def append_command(args: ChatCommandArgs,
                         input: CommandActionTokens) -> bool:
    message: str
    successful: bool = await args.database.appendCustomCommand(
        input.broadcaster, input.level, input.command, input.text, args.nick)
    if successful:
        message = '{user} -> {command} was appended successfully'
    else:
        message = ('{user} -> {command} was not appended successfully. The '
                   'command might not exist')
    args.chat.send(message.format(user=args.nick, command=input.command))
    return True


async def replace_command(args: ChatCommandArgs,
                          input: CommandActionTokens) -> bool:
    message: str
    successful: bool = await args.database.replaceCustomCommand(
        input.broadcaster, input.level, input.command, input.text, args.nick)
    if successful:
        message = '{user} -> {command} was replaced successfully'
    else:
        message = ('{user} -> {command} was not replaced successfully. The '
                   'command might not exist')
    args.chat.send(message.format(user=args.nick, command=input.command))
    return True


async def delete_command(args: ChatCommandArgs,
                         input: CommandActionTokens) -> bool:
    message: str
    successful: bool = await args.database.deleteCustomCommand(
        input.broadcaster, input.level, input.command, args.nick)
    if successful:
        message = '{user} -> {command} was removed successfully'
    else:
        message = ('{user} -> {command} was not removed successfully. The '
                   'command might not exist')
    args.chat.send(message.format(user=args.nick, command=input.command))
    return True


@permission('broadcaster')
async def command_property(args: ChatCommandArgs,
                           input: CommandActionTokens) -> bool:
    if not input.text:
        return False
    parts: List[Optional[str]] = input.text.split(None, 1)
    if len(parts) < 2:
        parts.append(None)
    property, value = parts
    if property not in lists.custom.properties:
        args.chat.send("{user} -> The property '{property}' does not "
                       'exist'.format(user=args.nick, property=property))
        return True
    if args.database.processCustomCommandProperty(
            input.broadcaster, input.level, input.command, property,
            value):
        if value is None:
            message = '{user} -> {command} with {property} has been unset'
        else:
            message = ('{user} -> {command} with {property} has been set with '
                       'the value of {value}')
    else:
        message = '{user} -> {command} with {property} could not be processed'
    args.chat.send(message.format(user=args.nick, command=input.command,
                                  property=property, value=value))
    return True


async def raw_command(args: ChatCommandArgs,
                      input: CommandActionTokens) -> bool:
    command: Optional[str]
    command = await args.database.getCustomCommand(
        input.broadcaster, input.level, input.command)
    message: str
    if command is None:
        message = '{user} -> {command} does not exist'
        args.chat.send(message.format(user=args.nick, command=input.command))
    else:
        utils.whisper(args.nick,
                      textwrap.wrap(command, width=bot.config.messageLimit))
    return True


async def level_command(args: ChatCommandArgs,
                        input: CommandActionTokens) -> bool:
    permission: str = input.text.lower()
    if permission not in custom.permissions:
        message = '{user} -> {inputLevel} is an invalid permission'
    elif args.database.levelCustomCommand(
            input.broadcaster, input.level, input.command, args.nick,
            custom.permissions[permission]):
        message = '{user} -> {command} changed permission successfully'
    else:
        message = ('{user} -> {command} was not changed successfully. The '
                   'command might not exist or there is a command with that '
                   'level existing')
    args.chat.send(message.format(user=args.nick, command=input.command,
                                  inputLevel=input.text))
    return True


async def rename_command(args: ChatCommandArgs,
                         input: CommandActionTokens) -> bool:
    newCommand: str = input.text and input.text.split(None, 1)[0]
    message: str
    if not newCommand:
        message = '{user} -> Please specify a command to rename to'
    elif args.database.renameCustomCommand(
            input.broadcaster, input.level, input.command, args.nick,
            newCommand):
        message = ('{user} -> {command} was renamed to successfully to '
                   '{newcommand}')
    else:
        message = ('{user} -> {command} was not renamed successfully to '
                   '{newcommand}. The command might not exist or there is a '
                   'command already existing')
    args.chat.send(message.format(user=args.nick, command=input.command,
                                  newcommand=newCommand))
    return True
