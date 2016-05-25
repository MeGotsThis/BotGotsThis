from ..library import custom, timeout
from ...params.argument import CustomFieldArgs, CustomProcessArgs
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
        return
    
    com, action, level, command, fullText = r
    broadcaster = args.chat.channel
    if com == '!global':
        broadcaster = '#global'
    
    if (args.database.hasFeature(args.chat.channel, 'nocustom') and
        broadcaster != '#global'):
        return False
        
    msg = None
    if level == False:
        msg = args.nick + ' -> Invalid level, command ignored'
        args.chat.sendMessage(msg)
        return
    if level:
        if level not in args.permissions:
            msg = args.nick + ' -> Invalid level, command ignored'
            args.chat.sendMessage(msg)
            return
        elif not args.permissions[level]:
            msg = args.nick + ' -> You do not have permission to set that level'
            args.chat.sendMessage(msg)
            return
    
    if action in ['property'] and args.permissions.broadcaster and fullText:
        parts = fullText.split(None, 1)
        if len(parts) < 2:
            parts.append(None)
        prop, value = parts
        if prop not in custom.properties:
            msg = args.nick + ' -> That property does not exist'
            args.chat.sendMessage(msg)
            return
        result = args.database.processCustomCommandProperty(
            broadcaster, level, command, prop, value)
        if result:
            if value is None:
                msg = command + ' with ' + prop + ' has been unset'
                args.chat.sendMessage(msg)
            else:
                msg = command + ' with ' + prop + ' has been set with the '
                msg += 'value of ' + value
                args.chat.sendMessage(msg)
        else:
            msg = command + ' with ' + prop + ' could not be processed'
            args.chat.sendMessage(msg)
    elif action in ['add', 'insert', 'new']:
        result = args.database.insertCustomCommand(
            broadcaster, level, command, fullText, args.nick)
        if result:
            args.chat.sendMessage(command + ' was added successfully')
        else:
            msg = command + ' was not added successfully. There might be an '
            msg += 'existing command'
            args.chat.sendMessage(msg)
    elif action in ['edit', 'update']:
        params = broadcaster, level, command, fullText, args.nick
        result = args.database.updateCustomCommand(*params)
        if result:
            msg = command + ' was updated successfully'
            args.chat.sendMessage(msg)
        else:
            msg = command + ' was not updated successfully. The command might '
            msg += 'not exist'
            args.chat.sendMessage(msg)
    elif action in ['replace', 'override']:
        params = broadcaster, level, command, fullText, args.nick
        result = args.database.replaceCustomCommand(*params)
        if result:
            args.chat.sendMessage(command + ' was updated successfully')
        else:
            msg = command + ' was not updated successfully. The command might '
            msg += 'not exist'
            args.chat.sendMessage(msg)
    elif action in ['append']:
        params = broadcaster, level, command, fullText, args.nick
        result = args.database.appendCustomCommand(*params)
        if result:
            msg = command + ' was appended successfully'
            args.chat.sendMessage(msg)
        else:
            msg = command + ' was not appended successfully. The command might '
            msg += 'not exist'
            args.chat.sendMessage(msg)
    elif action in ['del', 'delete', 'rem', 'remove',]:
        params = broadcaster, level, command, args.nick
        result = args.database.deleteCustomCommand(*params)
        if result:
            args.chat.sendMessage(command + ' was removed successfully')
        else:
            msg = command + ' was not removed successfully. The command might '
            msg += 'not exist'
            args.chat.sendMessage(msg)
