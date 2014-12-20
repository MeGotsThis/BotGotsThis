import database.factory
import ircbot.irc
import threading
import re

def customCommands(channelData, nick, message, msgParts, permissions):
    command = msgParts[0].lower()
    params = channelData, command, nick, permissions, message
    threading.Thread(target=threadCustomCommand, args=params).start()
    return True

def threadCustomCommand(channelData, command, nick, permissions, originalMsg):
    channel = channelData.channel[1:]
    message = None
    
    with database.factory.getDatabase() as db:
        commands = db.getChatCommands(channel, command)
    
    permissionsSet = ['', 'turbo', 'subscriber', 'moderator', 'broadcaster',
                      'globalMod', 'admin', 'staff', 'owner',]
    for perm in permissionsSet:
        if not perm or permissions[perm]:
            if perm in commands['#global']:
                message = commands['#global'][perm]
            if perm in commands[channel]:
                message = commands[channel][perm]
    
    if message:
        message.replace('{user}', nick)
        message.replace('{query}', originalMsg)
        def paramReplace(matchobj):
            matchParts = matchobj.groups()
            if matchParts[1] is not None:
                msgParts = originalMsg.split()
                i = int(matchParts[1])
                if i >= len(msgParts):
                    return ''
                if matchParts[2] is None:
                    return msgParts[i]
                else:
                    s = originalMsg.split(None, i)[i]
                    j = int(matchParts[3])
                    if len(msgParts) <= j:
                        return s.rsplit(None, len(msgParts) - j - 1)[0]
                    else:
                        return s
            if matchParts[4] is not None:
                i = int(matchParts[5])
                msgParts = originalMsg.split(None, i)
                if i < len(msgParts):
                    return msgParts[i]
                else:
                    return ''
            if matchParts[6] is not None:
                j = int(matchParts[7])
                msgParts = originalMsg.split()
                if j == 0:
                    return originalMsg.split(None)[0]
                elif len(msgParts) >= 2:
                    if len(msgParts) <= j:
                        return originalMsg.split(None, 1)[1]
                    else:
                        splits = len(msgParts) - j - 1
                        msg = originalMsg.rsplit(None, splits)[0]
                        return msg.split(None, 1)[1]
                else:
                    return ''
            return ''
        pattern = r'(\{(\d+)(-(\d+))?\})|(\{(\d+)-\})|(\{-(\d+)\})'
        message = re.sub(pattern, paramReplace, message)
        channelData.sendMessage(message)

def commandCommand(channelData, nick, message, msgParts, permissions):
    if len(msgParts) < 3:
        return False
    
    com, action, level, command, fullText = parseCommandMessageInput(message)
    broadcaster = channelData.channel[1:]
    if com == '!global':
        broadcaster = '#global'
    
    params = [channelData, broadcaster, nick, permissions,
              action, level, command, fullText]
    threading.Thread(target=threadCommand, args=params).start()

def threadCommand(channelData, broadcaster, nick, permissions,
                  action, level, command, fullText):
    if level == False:
        channelData.sendMessage(nick + ' -> Invalid level, command ignored')
        return
    if level:
        if level not in permissions:
            channelData.sendMessage(
                nick + ' -> Invalid level, command ignored')
            return
        elif not permissions[level]:
            channelData.sendMessage(
                nick + ' -> You do not have permission to set that level')
            return
    
    if action in ['add', 'insert', 'new']:
        if not fullText:
            channelData.sendMessage(
                'You need to specify some text for that command')
            return
        
        with database.factory.getDatabase() as db:
            result = db.insertCustomCommand(
                broadcaster, level, command, fullText)
            if result:
                channelData.sendMessage(command + ' was added successfully')
            else:
                channelData.sendMessage(
                    command + ' was not added successfully. There might be '
                    'an existing command')
    elif action in ['edit', 'update']:
        if not fullText:
            channelData.sendMessage(
                'You need to specify some text for that command')
            return
        
        with database.factory.getDatabase() as db:
            result = db.updateCustomCommand(
                broadcaster, level, command, fullText)
            if result:
                channelData.sendMessage(
                    command + ' was updated successfully')
            else:
                channelData.sendMessage(
                    command + ' was not updated successfully. The command '
                    'might not exist')
    elif action in ['replace', 'override']:
        with database.factory.getDatabase() as db:
            result = db.replaceCustomCommand(
                broadcaster, level, command, fullText)
            if result:
                channelData.sendMessage(
                    command + ' was updated successfully')
            else:
                channelData.sendMessage(
                    command + ' was not updated successfully. The command '
                    'might not exist')
    elif action in ['del', 'delete', 'rem', 'remove',]:
        with database.factory.getDatabase() as db:
            result = db.deleteCustomCommand(broadcaster, level, command)
            if result:
                channelData.sendMessage(
                    command + ' was removed successfully')
            else:
                channelData.sendMessage(
                    command + ' was not removed successfully. The command '
                    'might not exist')

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
            mparts.append(None)
        command, fullText = mparts
        
        return (originalCommand, action.lower(), level, command, fullText)
    except Exception:
        return None
