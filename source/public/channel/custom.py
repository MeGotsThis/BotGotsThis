from ..library import custom, timeout
from ...data.argument import CustomFieldArgs, CustomProcessArgs
from bot import config
from collections import defaultdict
import datetime
import lists.custom

def customCommands(args):
    customMessage = None
    
    if args.database.hasFeature(args.chat.channel, 'nocustom'):
        return False
    
    commands = args.database.getChatCommands(args.chat.channel,
                                             args.message.command)
    hasTextConvert = args.database.hasFeature(args.chat.channel, 'textconvert')
    
    permissionsSet = ['', 'turbo', 'subscriber', 'moderator', 'broadcaster',
                      'globalMod', 'admin', 'staff', 'owner',]
    level = None
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
            for part in custom.parseFormatMessage(str(customMessage)):
                plain, field, format, prefix, suffix, *_ = part
                param, default, original = _
                final.append(plain)
                try:
                    if field is not None:
                        fieldArgument = CustomFieldArgs(
                            str(field), str(param), str(prefix), str(suffix),
                            str(default), args.message, args.chat.channel,
                            args.nick, args.timestamp)
                        string = custom.fieldString(fieldArgument)
                        if string is not None:
                            string = custom.format(str(string), str(format),
                                                   hasTextConvert)
                        else:
                            string = str(original)
                        final.append(str(string))
                except Exception as e:
                    final.append(str(original))
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

def commandCommand(args):
    if len(args.message) < 3:
        return False
    
    r = custom.parseCommandMessageInput(args.message)
    if r is None:
        return False
    
    com, action, level, command, fullText = r
    broadcaster = args.chat.channel
    if com == '!global':
        broadcaster = '#global'
    
    if (args.database.hasFeature(args.chat.channel, 'nocustom') and
        broadcaster != '#global'):
        return False
        
    msg = None
    if level == False:
        args.chat.sendMessage('{user} -> Invalid level, command '
                              'ignored'.format(user=args.nick))
        return True
    if level:
        if level not in args.permissions:
            args.chat.sendMessage('{user} -> Invalid level, command '
                                  'ignored'.format(user=args.nick))
            return True
        elif not args.permissions[level]:
            args.chat.sendMessage('{user} -> You do not have permission to '
                                  'set that level'.format(user=args.nick))
            return True
    
    if action in ['property'] and args.permissions.broadcaster and fullText:
        parts = fullText.split(None, 1)
        if len(parts) < 2:
            parts.append(None)
        prop, value = parts
        if prop not in custom.properties:
            args.chat.sendMessage('{user} -> That property does not '
                                  'exist'.format(user=args.nick))
            return True
        if args.database.processCustomCommandProperty(
                broadcaster, level, command, prop, value):
            if value is None:
                msg = '{command} with {property} has been unset'
            else:
                msg = ('{command} with {property} has been set with the value '
                       'of {value}')
        else:
            msg = '{command} with {property} could not be processed'
        args.chat.sendMessage(
            msg.format(command=command, property=prop, value=value))
        return True
    elif action in ['add', 'insert', 'new']:
        if args.database.insertCustomCommand(
                broadcaster, level, command, fullText, args.nick):
            msg = '{command} was added successfully'
        else:
            msg = ('{command} was not added successfully. There might be an '
                   'existing command')
    elif action in ['edit', 'update']:
        if args.database.updateCustomCommand(
                broadcaster, level, command, fullText, args.nick):
            msg = '{command} was updated successfully'
        else:
            msg = ('{command} was not updated successfully. The command might '
                   'not exist')
    elif action in ['replace', 'override']:
        if args.database.replaceCustomCommand(
                broadcaster, level, command, fullText, args.nick):
            msg = '{command} was updated successfully'
        else:
            msg = ('{command} was not updated successfully. The command might '
                   'not exist')
    elif action in ['append']:
        if args.database.appendCustomCommand(
                broadcaster, level, command, fullText, args.nick):
            msg = '{command} was appended successfully'
        else:
            msg = ('{command} was not appended successfully. The command '
                   'might not exist')
    elif action in ['del', 'delete', 'rem', 'remove',]:
        if args.database.deleteCustomCommand(
                broadcaster, level, command, args.nick):
            msg = '{command} was removed successfully'
        else:
            msg = ('{command} was not removed successfully. The command might '
                   'not exist')
    else:
        return False
    args.chat.sendMessage(msg.format(command=command))
    return True
