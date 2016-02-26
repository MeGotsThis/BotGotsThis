from ..common import charConvert, timeout
from bot import config
from lists import custom
import datetime

def customCommands(db, chat, tags, nick, message, msgParts, permissions, now):
    command = msgParts[0].lower()
    customMessage = None
    
    if db.hasFeature(chat.channel, 'nocustom'):
        return False
    
    commands = db.getChatCommands(chat.channel, command)
    hasTextConvert = db.hasFeature(chat.channel, 'textconvert')
    
    permissionsSet = ['', 'turbo', 'subscriber', 'moderator', 'broadcaster',
                      'globalMod', 'admin', 'staff', 'owner',]
    level = None
    for perm in permissionsSet:
        if not perm or permissions[perm]:
            if perm in commands['#global']:
                customMessage = commands['#global'][perm]
                level = perm
            if perm in commands[chat.channel]:
                customMessage = commands[chat.channel][perm]
                level = perm
    
    if customMessage:
        currentTime = datetime.datetime.utcnow()
        cooldown = datetime.timedelta(seconds=config.customMessageCooldown)
        if (not permissions['moderator'] and
            'customCommand' in chat.sessionData):
            since = currentTime - chat.sessionData['customCommand']
            if since < cooldown:
                return
        chat.sessionData['customCommand'] = currentTime

        cooldown = datetime.timedelta(seconds=config.customMessageUserCooldown)
        if 'customUserCommand' not in chat.sessionData:
            chat.sessionData['customUserCommand'] = {}
        if (not permissions['moderator'] and
            nick in chat.sessionData['customUserCommand']):
            oldTime = chat.sessionData['customUserCommand'][nick]
            since = currentTime - oldTime
            if since < cooldown:
                return
        chat.sessionData['customUserCommand'][nick] = currentTime
        
        query = str(message.split(None, 1)[1]) if len(msgParts) > 1 else ''
        final = []
        try:
            for part in _parseFormatMessage(str(customMessage)):
                plain, field, format, prefix, suffix, *_ = part
                param, default, original = _
                final.append(plain)
                try:
                    if field is not None:
                        params = str(field), str(param), str(prefix),
                        params += str(suffix),str(default), message,
                        params += msgParts, chat.channel, nick, query, now
                        string = _getString(*params)
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
        for process in custom.postProcess:
            process(db, chat, tags, nick, permissions, level, command, msgs)
        chat.sendMulipleMessages(msgs)
        if permissions['channelModerator']:
            timeout.recordTimeoutFromCommand(db, chat, nick, msgs, message)

def commandCommand(db, chat, tags, nick, message, msgParts, permissions, now):
    if len(msgParts) < 3:
        return False
    
    r = parseCommandMessageInput(message)
    if r is None:
        return
    
    com, action, level, command, fullText = r
    broadcaster = chat.channel
    if com == '!global':
        broadcaster = '#global'
    
    if (db.hasFeature(chat.channel, 'nocustom') and
        broadcaster != '#global'):
        return False
        
    msg = None
    if level == False:
        msg = nick + ' -> Invalid level, command ignored'
        chat.sendMessage(msg)
        return
    if level:
        if level not in permissions:
            msg = nick + ' -> Invalid level, command ignored'
            chat.sendMessage(msg)
            return
        elif not permissions[level]:
            msg = nick + ' -> You do not have permission to set that level'
            chat.sendMessage(msg)
            return
    
    if action in ['property'] and permissions['broadcaster'] and fullText:
        parts = fullText.split(None, 1)
        if len(parts) < 2:
            parts.append(None)
        prop, value = parts
        if prop not in custom.properties:
            msg = nick + ' -> That property does not exist'
            chat.sendMessage(msg)
            return
        result = db.processCustomCommandProperty(
            broadcaster, level, command, prop, value)
        if result:
            if value is None:
                chat.sendMessage(command + ' with ' + prop + ' has been unset')
            else:
                msg = command + ' with ' + prop + ' has been set with the '
                msg += 'value of ' + value
                chat.sendMessage(msg)
        else:
            msg = command + ' with ' + prop + ' could not be processed'
            chat.sendMessage(msg)
    elif action in ['add', 'insert', 'new']:
        result = db.insertCustomCommand(
            broadcaster, level, command, fullText, nick)
        if result:
            chat.sendMessage(command + ' was added successfully')
        else:
            msg = command + ' was not added successfully. There might be an '
            msg += 'existing command'
            chat.sendMessage(msg)
    elif action in ['edit', 'update']:
        params = broadcaster, level, command, fullText, nick
        result = db.updateCustomCommand(*params)
        if result:
            msg = command + ' was updated successfully'
            chat.sendMessage(msg)
        else:
            msg = command + ' was not updated successfully. The command might '
            msg += 'not exist'
            chat.sendMessage(msg)
    elif action in ['replace', 'override']:
        params = broadcaster, level, command, fullText, nick
        result = db.replaceCustomCommand(*params)
        if result:
            chat.sendMessage(command + ' was updated successfully')
        else:
            msg = command + ' was not updated successfully. The command might '
            msg += 'not exist'
            chat.sendMessage(msg)
    elif action in ['append']:
        params = broadcaster, level, command, fullText, nick
        result = db.appendCustomCommand(*params)
        if result:
            msg = command + ' was appended successfully'
            chat.sendMessage(msg)
        else:
            msg = command + ' was not appended successfully. The command might '
            msg += 'not exist'
            chat.sendMessage(msg)
    elif action in ['del', 'delete', 'rem', 'remove',]:
        result = db.deleteCustomCommand(broadcaster, level, command, nick)
        if result:
            chat.sendMessage(command + ' was removed successfully')
        else:
            msg = command + ' was not removed successfully. The command might '
            msg += 'not exist'
            chat.sendMessage(msg)

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
        m = message
        originalCommand, action, m = m.split(None, 2)
        level = None
        if m.startswith('level='):
            parseLevel, m = m.split(None, 1)
            level = parseLevel[len('level='):]
        if level in allowPermissions:
            level = allowPermissions[level]
        else:
            level = False
        mparts = m.split(None, 1)
        while len(mparts) < 2:
            mparts.append('')
        command, fullText = mparts
        
        return (originalCommand, action.lower(), level, command, fullText)
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

def _getString(field, param, prefix, suffix, default, message,  msgParts,
               channel, nick, query, now):
    for fieldConvert in custom.fields:
        result = fieldConvert(field, param, prefix, suffix, default, message,
                              msgParts, channel, nick, query, now)
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
