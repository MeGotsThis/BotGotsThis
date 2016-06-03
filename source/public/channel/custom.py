from ..library import custom, timeout
from ..library.chat import not_feature, permission, ownerChannel
from bot import config
from bot.data.argument import CustomFieldArgs, CustomProcessArgs
from collections import defaultdict
import datetime
import lists.custom

@not_feature('nocustom')
def customCommands(args):
    commands = args.database.getChatCommands(args.chat.channel,
                                             args.message.command)
    hasTextConvert = args.database.hasFeature(args.chat.channel, 'textconvert')
    
    permissionsSet = ['', 'turbo', 'subscriber', 'moderator', 'broadcaster',
                      'globalMod', 'admin', 'staff', 'owner',]
    level = None
    customMessage = None
    for perm in permissionsSet:
        if not perm or args.permissions[perm]:
            if perm in commands['#global']:
                customMessage = commands['#global'][perm]
                broadcaster = '#global'
                level = perm
            if perm in commands[args.chat.channel]:
                customMessage = commands[args.chat.channel][perm]
                broadcaster = args.chat.channel
                level = perm
    
    if customMessage:
        currentTime = datetime.datetime.utcnow()
        cooldown = datetime.timedelta(seconds=config.customMessageCooldown)
        if (not args.permissions.moderator and
            'customCommand' in args.chat.sessionData):
            since = currentTime - args.chat.sessionData['customCommand']
            if since < cooldown:
                return
        args.chat.sessionData['customCommand'] = currentTime

        cooldown = datetime.timedelta(seconds=config.customMessageUserCooldown)
        if 'customUserCommand' not in args.chat.sessionData:
            args.chat.sessionData['customUserCommand'] = defaultdict(
                lambda: datetime.datetime.min)
        if not args.permissions.moderator:
            oldTime = args.chat.sessionData['customUserCommand'][args.nick]
            since = currentTime - oldTime
            if since < cooldown:
                return
        args.chat.sessionData['customUserCommand'][args.nick] = currentTime
        
        final = []
        try:
            for formats in custom.parseFormatMessage(customMessage):
                final.append(formats.plainText)
                try:
                    if formats.field is not None:
                        fieldArgument = CustomFieldArgs(
                            formats.field, formats.param, formats.prefix,
                            formats.suffix, formats.default, args.message,
                            args.chat.channel, args.nick, args.timestamp)
                        string = custom.fieldString(fieldArgument)
                        if string is not None:
                            string = custom.format(string, formats.format,
                                                   hasTextConvert)
                        else:
                            string = formats.original
                        final.append(string)
                except Exception as e:
                    final.append(formats.original)
        except Exception as e:
            final = [str(customMessage)]
        msgs = [''.join(final)]
        processArgument = CustomProcessArgs(
            args.database, args.chat, args.tags, args.nick, args.permissions,
            broadcaster, level, args.message.command, msgs)
        for process in lists.custom.postProcess:
            process(processArgument)
        args.chat.sendMulipleMessages(msgs)
        if args.permissions.chatModerator:
            timeout.recordTimeoutFromCommand(args.database, args.chat,
                                             args.nick, msgs, args.message)

@ownerChannel
@permission('admin')
def commandGlobal(args):
    return processCommand(args)

@not_feature('nocustom')
@permission('moderator')
def commandCommand(args):
    return processCommand(args)

def processCommand(args):
    if len(args.message) < 3:
        return False
    
    input = custom.parseCommandMessageInput(args.message)
    if r is None:
        return False
    
    com, action, level, command, fullText = r
    broadcaster = args.chat.channel
    if input.called == '!global':
        broadcaster = '#global'
    
    msg = None
    if input.level == False:
        args.chat.sendMessage('{user} -> Invalid level, command '
                              'ignored'.format(user=args.nick))
        return True
    if input.level:
        if input.level not in args.permissions:
            args.chat.sendMessage('{user} -> Invalid level, command '
                                  'ignored'.format(user=args.nick))
            return True
        elif not args.permissions[input.level]:
            args.chat.sendMessage('{user} -> You do not have permission to '
                                  'set that level'.format(user=args.nick))
            return True
    
    if (input.action in ['property'] and args.permissions.broadcaster
            and input.text):
        parts = input.text.split(None, 1)
        if len(parts) < 2:
            parts.append(None)
        prop, value = parts
        if prop not in custom.properties:
            args.chat.sendMessage('{user} -> That property does not '
                                  'exist'.format(user=args.nick))
            return True
        if args.database.processCustomCommandProperty(
                broadcaster, input.level, input.command, prop, value):
            if value is None:
                msg = '{command} with {property} has been unset'
            else:
                msg = ('{command} with {property} has been set with the value '
                       'of {value}')
        else:
            msg = '{command} with {property} could not be processed'
        args.chat.sendMessage(
            msg.format(command=input.command, property=prop, value=value))
        return True
    elif input.action in ['add', 'insert', 'new']:
        if args.database.insertCustomCommand(
                broadcaster, input.level, input.command, input.text,
                args.nick):
            msg = '{command} was added successfully'
        else:
            msg = ('{command} was not added successfully. There might be an '
                   'existing command')
    elif input.action in ['edit', 'update']:
        if args.database.updateCustomCommand(
                broadcaster, input.level, input.command, input.text,
                args.nick):
            msg = '{command} was updated successfully'
        else:
            msg = ('{command} was not updated successfully. The command might '
                   'not exist')
    elif input.action in ['replace', 'override']:
        if args.database.replaceCustomCommand(
                broadcaster, input.level, input.command, input.text,
                args.nick):
            msg = '{command} was updated successfully'
        else:
            msg = ('{command} was not updated successfully. The command might '
                   'not exist')
    elif input.action in ['append']:
        if args.database.appendCustomCommand(
                broadcaster, input.level, input.command, input.text,
                args.nick):
            msg = '{command} was appended successfully'
        else:
            msg = ('{command} was not appended successfully. The command '
                   'might not exist')
    elif input.action in ['del', 'delete', 'rem', 'remove',]:
        if args.database.deleteCustomCommand(
                broadcaster, input.level, input.command, args.nick):
            msg = '{command} was removed successfully'
        else:
            msg = ('{command} was not removed successfully. The command might '
                   'not exist')
    else:
        return False
    args.chat.sendMessage(msg.format(command=input.command))
    return True
