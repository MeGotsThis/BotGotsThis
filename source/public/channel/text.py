from . import charConvert
from bot import config
from lists import custom
import datetime

def customCommands(db, channel, nick, message, msgParts, permissions):
    command = msgParts[0].lower()
    message = None
    
    if db.hasFeature(channel.channel, 'nocustom'):
        return False
    
    commands = db.getChatCommands(channel.channel, command)
    hasTextConvert = db.hasFeature(channel.channel, 'textconvert')
    
    permissionsSet = ['', 'turbo', 'subscriber', 'moderator', 'broadcaster',
                      'globalMod', 'admin', 'staff', 'owner',]
    for perm in permissionsSet:
        if not perm or permissions[perm]:
            if perm in commands['#global']:
                message = commands['#global'][perm]
            if perm in commands[channel.channel]:
                message = commands[channel.channel][perm]
    
    if message:
        currentTime = datetime.datetime.utcnow()
        cooldown = datetime.timedelta(seconds=config.customMessageCooldown)
        if (not permissions['moderator'] and
            'customCommand' in channel.sessionData):
            since = currentTime - channel.sessionData['customCommand']
            if since < cooldown:
                return
        channel.sessionData['customCommand'] = currentTime

        cooldown = datetime.timedelta(seconds=config.customMessageUserCooldown)
        if 'customUserCommand' not in channel.sessionData:
            channel.sessionData['customUserCommand'] = {}
        if (not permissions['moderator'] and
            nick in channel.sessionData['customUserCommand']):
            oldTime = channel.sessionData['customUserCommand'][nick]
            since = currentTime - oldTime
            if since < cooldown:
                return
        channel.sessionData['customUserCommand'][nick] = currentTime
        
        query = str(originalMsg.split(None, 1)[1]) if len(msgParts) > 1 else ''
        final = []
        try:
            for part in _parseFormatMessage(str(message)):
                plain, field, format, param, default, original = part
                final.append(plain)
                if field is not None:
                    params = str(field), str(param), str(default), originalMsg,
                    params += msgParts, channel.channel, nick, query,
                    string = _getString(*params)
                    if string is not None:
                        string = _formatString(str(string), str(format),
                                               hasTextConvert)
                    else:
                        string = str(original)
                    final.append(str(string))
        except:
            final.append(str(message))
        channel.sendMessage(''.join(final))

def commandCommand(db, channel, nick, message, msgParts, permissions):
    if len(msgParts) < 3:
        return False
    
    r = parseCommandMessageInput(message)
    if r is None:
        return
    
    com, action, level, command, fullText = r
    broadcaster = channel.channel
    if com == '!global':
        broadcaster = '#global'
    
    if (db.hasFeature(channel.channel, 'nocustom') and
        broadcaster != '#global'):
        return False
        
    msg = None
    if level == False:
        msg = nick + ' -> Invalid level, command ignored'
        channel.sendMessage(msg)
        return
    if level:
        if level not in permissions:
            msg = nick + ' -> Invalid level, command ignored'
            channel.sendMessage(msg)
            return
        elif not permissions[level]:
            msg = nick + ' -> You do not have permission to set that level'
            channel.sendMessage(msg)
            return
        
    if action in ['add', 'insert', 'new']:
        result = db.insertCustomCommand(
            broadcaster, level, command, fullText, nick)
        if result:
            channel.sendMessage(command + ' was added successfully')
        else:
            msg = command + ' was not added successfully. There might be an '
            msg += 'existing command'
            channel.sendMessage(msg)
    elif action in ['edit', 'update']:
        params = broadcaster, level, command, fullText, nick
        result = db.updateCustomCommand(*params)
        if result:
            msg = command + ' was updated successfully'
            channel.sendMessage(msg)
        else:
            msg = command + ' was not updated successfully. The command might '
            msg += 'not exist'
            channel.sendMessage(msg)
    elif action in ['replace', 'override']:
        params = broadcaster, level, command, fullText, nick
        result = db.replaceCustomCommand(*params)
        if result:
            channel.sendMessage(command + ' was updated successfully')
        else:
            msg = command + ' was not updated successfully. The command might '
            msg += 'not exist'
            channel.sendMessage(msg)
    elif action in ['del', 'delete', 'rem', 'remove',]:
        result = db.deleteCustomCommand(broadcaster, level, command, nick)
        if result:
            channel.sendMessage(command + ' was removed successfully')
        else:
            msg = command + ' was not removed successfully. The command might '
            msg += 'not exist'
            channel.sendMessage(msg)

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
                p = ''.join(noFormat), None, None, None, None, None
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
                       ''.join(param),
                       ''.join(default),
                       original))
        
    return parsed

def _getString(field, param, default, message, msgParts, channel, nick, query):
    for fieldConvert in custom.fields:
        result = fieldConvert(field, param, default, message, msgParts,
                              channel, nick, query)
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
    return string
