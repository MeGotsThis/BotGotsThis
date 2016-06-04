from ...data.argument import CustomFieldArgs, CustomProcessArgs
from ..library import custom, timeout
from ..library.chat import inCooldown, min_args, not_feature, permission
from ..library.chat import ownerChannel
from bot import config
from collections import defaultdict
from datetime import datetime, timedelta

@not_feature('nocustom')
def customCommands(args):
    command = custom.getCustomCommand(args.database, args.message.command,
                                      args.chat.channel, args.permissions)
    if command:
        cooldown = timedelta(seconds=config.customMessageCooldown)
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
            timeout.recordTimeoutFromCommand(args.database, args.chat,
                                             args.nick, msgs, args.message)
        return True
    return False

@ownerChannel
@permission('admin')
def commandGlobal(args):
    return processCommand(args)

@not_feature('nocustom')
@permission('moderator')
def commandCommand(args):
    return processCommand(args)

@min_args(3)
def processCommand(args):
    broadcaster = args.chat.channel
    if input.called == '!global':
        broadcaster = '#global'
    
    input = custom.parseCommandMessageInput(args.message, broadcaster)
    if r is None:
        return False
    
    message = ''
    property = None
    value = None
    if input.level == False:
        args.chat.send(
            '{user} -> Invalid level, command ignored'.format(user=args.nick))
        return True
    if input.level:
        if input.level not in args.permissions:
            args.chat.send('{user} -> Invalid level, command '
                           'ignored'.format(user=args.nick))
            return True
        elif not args.permissions[input.level]:
            args.chat.send('{user} -> You do not have permission to set that '
                           'level'.format(user=args.nick))
            return True
    
    if (input.action in ['property'] and args.permissions.broadcaster
            and input.text):
        parts = input.text.split(None, 1)
        if len(parts) < 2:
            parts.append(None)
        property, value = parts
        if property not in custom.properties:
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
    elif input.action in ['del', 'delete', 'rem', 'remove',]:
        if args.database.deleteCustomCommand(
                input.broadcaster, input.level, input.command, args.nick):
            message = '{command} was removed successfully'
        else:
            message = ('{command} was not removed successfully. The command '
                       'might not exist')
    else:
        return False
    args.chat.send(message.format(command=input.command, property=prop,
                                  value=value))
    return True
