from ..library import charConvert, timeout
from ...params.argument import CustomFieldsArgs, CustomProcessArgs
from bot import config
from collections import defaultdict
from lists import custom
import datetime

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
            for part in _parseFormatMessage(str(customMessage)):
                plain, field, format, prefix, suffix, *_ = part
                param, default, original = _
                final.append(plain)
                try:
                    if field is not None:
                        fieldArgument = CustomFieldArgs(
                            str(field), str(param), str(prefix), str(suffix),
                            str(default), args.message, args.chat.channel,
                            args.nick, args.timestamp)
                        string = _getString(fieldArgument)
                        if string is not None:
                            string = _formatString(str(string), str(format),
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
        for process in custom.postProcess:
            process(processArgument)
        args.chat.sendMulipleMessages(msgs)
        if args.permissions.chatModerator:
            timeout.recordTimeoutFromCommand(args.database, args.chat, nick,
                                             msgs, args.message)

def commandCommand(args):
    if len(args.message) < 3:
        return False
    
    r = parseCommandMessageInput(args.message)
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

def parseCommandMessageInput(message):
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
        level = None
        if message[2].startswith('level='):
            i = 3
            level = message[2][len('level='):]
        if level in allowPermissions:
            level = allowPermissions[level]
        else:
            level = False
        command = message[i]
        fullText = message[i+1:]
        
        return (message.command, action, level, command, fullText)
    except:
        return None

def _parseFormatMessage(message):
    # Format: {field:format<prefix>suffix@param!default}
    parsed = []
    i = 0
    length = len(message)
    
    while True:
        noFormat = []
        while i < length:
            char = message[i]
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
                p = (''.join(noFormat),) + (None,) * 7
                parsed.append(p)
            break
        
        s = i
        i += 1
        if i == length:
            raise ValueError()
        
        field = []
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

        format = []
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

        prefix = []
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

        suffix = []
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

        param = []
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

        default = []
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
        
        parsed.append((''.join(noFormat),
                       ''.join(field),
                       ''.join(format),
                       ''.join(prefix),
                       ''.join(suffix),
                       ''.join(param),
                       ''.join(default),
                       original))
        
    return parsed

def _getString(args):
    for fieldConvert in custom.fields:
        result = fieldConvert(args)
        if result is not None:
            return result

    return None

def _formatString(string, format, hasTextConvert):
    format = format.lower()
    if hasTextConvert:
        if format == 'ascii':
            return charConvert.allToAscii(string)
        if format == 'full':
            return charConvert.asciiToFullWidth(string)
        if format == 'parenthesized':
            return charConvert.asciiToParenthesized(string)
        if format == 'circled':
            return charConvert.asciiToCircled(string)
        if format == 'smallcaps':
            return charConvert.asciiToSmallCaps(string)
        if format == 'upsidedown':
            return charConvert.asciiToUpsideDown(string)
        if format in ['serifbold', 'serif-bold']:
            return charConvert.asciiToSerifBold(string)
        if format in ['serifitalic', 'serif-italic']:
            return charConvert.asciiToSerifItalic(string)
        if format in ['serifbolditalic', 'serif-bold-italic',
                      'serif-bolditalic', 'serifbold-italic',
                      'serifitalicbold', 'serif-italic-bold',
                      'serifitalic-bold', 'serif-italicbold',]:
            return charConvert.asciiToSerifBoldItalic(string)
        if format == 'sanserif':
            return charConvert.asciiToSanSerif(string)
        if format in ['sanserifbold', 'sanserif-bold', 'bold']:
            return charConvert.asciiToSanSerifBold(string)
        if format in ['sanserifitalic', 'sanserif-italic', 'italic']:
            return charConvert.asciiToSanSerifItalic(string)
        if format in ['sanserifbolditalic', 'sanserif-bold-italic',
                      'sanserif-bolditalic', 'sanserifbold-italic',
                      'sanserifitalicbold', 'sanserif-italic-bold',
                      'sanserifitalic-bold', 'sanserif-italicbold',
                      'bolditalic', 'bold-italic',
                      'italicbold', 'italic-bold']:
            return charConvert.asciiToSanSerifBoldItalic(string)
        if format in ['script', 'cursive']:
            return charConvert.asciiToScript(string)
        if format in ['scriptbold', 'cursivebold',
                      'script-bold', 'cursive-bold',]:
            return charConvert.asciiToScriptBold(string)
        if format == 'fraktur':
            return charConvert.asciiToFraktur(string)
        if format in ['frakturbold', 'fraktur-bold']:
            return charConvert.asciiToFrakturBold(string)
        if format == 'monospace':
            return charConvert.asciiToMonospace(string)
        if format == 'doublestruck':
            return charConvert.asciiToDoubleStruck(string)
    return string
