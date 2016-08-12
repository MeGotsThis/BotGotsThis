import bot.config
import lists.custom
import textwrap
from bot import utils
from ..library import chat, custom, timeout
from ..library.chat import min_args, not_feature, permission, ownerChannel
from ...data import ChatCommandArgs, CustomCommand, CommandActionTokens
from datetime import timedelta
from typing import Callable, Dict, List, Optional


@not_feature('nocustom')
def customCommands(args: ChatCommandArgs) -> bool:
    command = custom.get_command(args.database, args.message.command,
                                 args.chat.channel,
                                 args.permissions)  # type: Optional[CustomCommand]
    if command is not None:
        cooldown = timedelta(seconds=bot.config.customMessageCooldown)  # type: timedelta
        if chat.inCooldown(args, cooldown, 'customCommand', 'moderator'):
            return False

        cooldown = timedelta(seconds=bot.config.customMessageUserCooldown)
        if chat.in_user_cooldown(args, cooldown, 'customUserCommand',
                                 'moderator'):
            return False
        
        msgs = custom.create_messages(command, args)
        args.chat.send(msgs)
        if args.permissions.chatModerator:
            timeout.record_timeout(args.database, args.chat, args.nick, msgs,
                                   str(args.message), 'custom')
        return True
    return False


@ownerChannel
@permission('admin')
def commandGlobal(args: ChatCommandArgs) -> bool:
    return process_command(args, '#global')


@not_feature('nocustom')
@permission('moderator')
def commandCommand(args: ChatCommandArgs) -> bool:
    return process_command(args, args.chat.channel)


@min_args(3)
def process_command(args: ChatCommandArgs,
                    broadcaster: str) -> bool:
    input = custom.parse_action_message(
        args.message, broadcaster)  # type: Optional[CommandActionTokens]
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
        }  # type: Dict[str, Callable[[ChatCommandArgs, CommandActionTokens], bool]]
    if input.action in actions:
        return actions[input.action](args, input)
    else:
        return False


def insert_command(args: ChatCommandArgs,
                   input: CommandActionTokens) -> bool:
    if args.database.insertCustomCommand(
            input.broadcaster, input.level, input.command, input.text,
            args.nick):
        message = '{user} -> {command} was added successfully'
    else:
        message = ('{user} -> {command} was not added successfully. There '
                   'might be an existing command')
    args.chat.send(message.format(user=args.nick, command=input.command))
    return True


def update_command(args: ChatCommandArgs,
                   input: CommandActionTokens) -> bool:
    if args.database.updateCustomCommand(
            input.broadcaster, input.level, input.command, input.text,
            args.nick):
        message = '{user} -> {command} was updated successfully'
    else:
        message = ('{user} -> {command} was not updated successfully. The '
                   'command might not exist')
    args.chat.send(message.format(user=args.nick, command=input.command))
    return True


def append_command(args: ChatCommandArgs,
                   input: CommandActionTokens) -> bool:
    if args.database.appendCustomCommand(input.broadcaster, input.level,
                                         input.command, input.text, args.nick):
        message = '{user} -> {command} was appended successfully'
    else:
        message = ('{user} -> {command} was not appended successfully. The '
                   'command might not exist')
    args.chat.send(message.format(user=args.nick, command=input.command))
    return True


def replace_command(args: ChatCommandArgs,
                    input: CommandActionTokens) -> bool:
    if args.database.replaceCustomCommand(
            input.broadcaster, input.level, input.command, input.text,
            args.nick):
        message = '{user} -> {command} was replaced successfully'
    else:
        message = ('{user} -> {command} was not replaced successfully. The '
                   'command might not exist')
    args.chat.send(message.format(user=args.nick, command=input.command))
    return True


def delete_command(args: ChatCommandArgs,
                   input: CommandActionTokens) -> bool:
    if args.database.deleteCustomCommand(input.broadcaster, input.level,
                                         input.command, args.nick):
        message = '{user} -> {command} was removed successfully'
    else:
        message = ('{user} -> {command} was not removed successfully. The '
                   'command might not exist')
    args.chat.send(message.format(user=args.nick, command=input.command))
    return True


@permission('broadcaster')
def command_property(args: ChatCommandArgs,
                     input: CommandActionTokens) -> bool:
    if not input.text:
        return False
    parts = input.text.split(None, 1)  # type: List[Optional[str]]
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


def raw_command(args: ChatCommandArgs,
                input: CommandActionTokens) -> bool:
    command = args.database.getCustomCommand(input.broadcaster, input.level,
                                             input.command)  # type: Optional[str]
    if command is None:
        message = '{user} -> {command} does not exist'
        args.chat.send(message.format(user=args.nick, command=input.command))
    else:
        utils.whisper(args.nick,
                      textwrap.wrap(command, width=bot.config.messageLimit))
    return True


def level_command(args: ChatCommandArgs,
                  input: CommandActionTokens) -> bool:
    if input.text not in custom.permissions:
        message = '{user} -> {inputLevel} is an invalid permission'
    elif args.database.levelCustomCommand(
            input.broadcaster, input.level, input.command, args.nick,
            custom.permissions[input.text]):
        message = '{user} -> {command} changed permission successfully'
    else:
        message = ('{user} -> {command} was not changed successfully. The '
                   'command might not exist')
    args.chat.send(message.format(user=args.nick, command=input.command,
                                  inputLevel=input.text))
    return True
