import lists.custom
from ..library import custom, timeout
from ..library.chat import inCooldown, min_args, not_feature, permission
from ..library.chat import ownerChannel
from ...data import ChatCommandArgs, CustomCommand, CustomCommandTokens
from bot import config
from collections import defaultdict
from datetime import datetime, timedelta
from typing import List, Optional


@not_feature('nocustom')
def customCommands(args: ChatCommandArgs) -> bool:
    command = custom.getCustomCommand(args.database, args.message.command,
                                      args.chat.channel, args.permissions)
    if command:
        cooldown = timedelta(seconds=config.customMessageCooldown)  # type: timedelta
        if inCooldown(args, cooldown, 'customCommand', 'moderator'):
            return False

        cooldown = timedelta(seconds=config.customMessageUserCooldown)
        if 'customUserCommand' not in args.chat.sessionData:
            args.chat.sessionData['customUserCommand'] = defaultdict(
                lambda: datetime.min)
        if not args.permissions.moderator:
            oldTime = args.chat.sessionData['customUserCommand'][args.nick]
            since = args.timestamp - oldTime
            if since < cooldown:
                return False
        args.chat.sessionData['customUserCommand'][args.nick] = args.timestamp
        
        msgs = custom.createMessages(command, args)
        args.chat.send(msgs)
        if args.permissions.chatModerator:
            timeout.record_timeout(args.database, args.chat, args.nick, msgs,
                                   str(args.message), 'custom')
        return True
    return False


@ownerChannel
@permission('admin')
def commandGlobal(args: ChatCommandArgs) -> bool:
    return processCommand(args, '#global')


@not_feature('nocustom')
@permission('moderator')
def commandCommand(args: ChatCommandArgs) -> bool:
    return processCommand(args, args.chat.channel)


@min_args(3)
def processCommand(args: ChatCommandArgs, broadcaster: str) -> bool:
    input = custom.parseCommandInput(
        args.message, broadcaster)  # type: Optional[CustomCommandTokens]
    if input is None:
        return False

    message = ''  # type: str
    property = None  # type: Optional[str]
    value = None  # type: Optional[str]
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

    if (input.action in ['property'] and args.permissions.broadcaster
            and input.text):
        parts = input.text.split(None, 1)  # type: List[Optional[str]]
        if len(parts) < 2:
            parts.append(None)
        property, value = parts
        if property not in lists.custom.properties:
            args.chat.send('{user} -> That property does not '
                           'exist'.format(user=args.nick))
            return True
        if args.database.processCustomCommandProperty(
                input.broadcaster, input.level, input.command, property,
                value):
            if value is None:
                message = '{command} with {property} has been unset'
            else:
                message = ('{command} with {property} has been set with the '
                           'value of {value}')
        else:
            message = '{command} with {property} could not be processed'
    elif input.action in ['add', 'insert', 'new']:
        if args.database.insertCustomCommand(
                input.broadcaster, input.level, input.command, input.text,
                args.nick):
            message = '{command} was added successfully'
        else:
            message = ('{command} was not added successfully. There might be '
                       'an existing command')
    elif input.action in ['edit', 'update']:
        if args.database.updateCustomCommand(
                input.broadcaster, input.level, input.command, input.text,
                args.nick):
            message = '{command} was updated successfully'
        else:
            message = ('{command} was not updated successfully. The command '
                       'might not exist')
    elif input.action in ['replace', 'override']:
        if args.database.replaceCustomCommand(
                input.broadcaster, input.level, input.command, input.text,
                args.nick):
            message = '{command} was updated successfully'
        else:
            message = ('{command} was not updated successfully. The command '
                       'might not exist')
    elif input.action in ['append']:
        if args.database.appendCustomCommand(
                input.broadcaster, input.level, input.command, input.text,
                args.nick):
            message = '{command} was appended successfully'
        else:
            message = ('{command} was not appended successfully. The command '
                       'might not exist')
    elif input.action in ['del', 'delete', 'rem', 'remove']:
        if args.database.deleteCustomCommand(
                input.broadcaster, input.level, input.command, args.nick):
            message = '{command} was removed successfully'
        else:
            message = ('{command} was not removed successfully. The command '
                       'might not exist')
    else:
        return False
    args.chat.send(message.format(command=input.command, property=property,
                                  value=value))
    return True
