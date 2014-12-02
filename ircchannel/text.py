import database.factory
import ircbot.irc

def customCommands(channelThread, nick, message, msgParts, permissions):
    command = msgParts[0].lower()
    channel = channelThread.channel[1:]
    message = None
    
    with database.factory.getDatabase() as db:
        commands = db.getChatCommands(channel, command)
    
    permissionsSet = ['', 'moderator', 'broadcaster',
                      'admin', 'staff', 'owner',]
    for perm in permissionsSet:
        if not perm or permissions[perm]:
            if perm in commands['#global']:
                message = commands['#global'][perm]
            if perm in commands[channel]:
                message = commands[channel][perm]
    
    if message:
        channelThread.sendMessage(message)
        return True
    
    return False

def commandCommand(channelThread, nick, message, msgParts, permissions):
    if len(msgParts) < 3:
        return False
    
    action, level, command, fullText = parseCommandMessageInput(message)
    if level == False:
        channelThread.sendMessage(nick + ' -> Invalid level, command ignored')
        return True
    if level:
        if level not in permissions:
            channelThread.sendMessage(
                nick + ' -> Invalid level, command ignored')
            return True
        elif not permissions[level]:
            channelThread.sendMessage(
                nick + ' -> You do not have permission to set that level')
            return True
    
    if action in ['add', 'insert', 'new']:
        if not fullText:
            channelThread.sendMessage(
                'You need to specify some text for that command')
            return True
        
        with database.factory.getDatabase() as db:
            result = db.insertCustomCommand(
                channelThread.channel[1:], level, command, fullText)
            if result:
                channelThread.sendMessage(command + ' was added successfully')
            else:
                channelThread.sendMessage(
                    command + ' was not added successfully. There might be '
                    'an existing command')
        return True
    elif action in ['edit', 'update']:
        if not fullText:
            channelThread.sendMessage(
                'You need to specify some text for that command')
            return True
        
        with database.factory.getDatabase() as db:
            result = db.updateCustomCommand(
                channelThread.channel[1:], level, command, fullText)
            if result:
                channelThread.sendMessage(
                    command + ' was updated successfully')
            else:
                channelThread.sendMessage(
                    command + ' was not updated successfully. The command '
                    'might not exist')
        return True
    elif action in ['replace', 'override']:
        with database.factory.getDatabase() as db:
            result = db.replaceCustomCommand(
                channelThread.channel[1:], level, command, fullText)
            if result:
                channelThread.sendMessage(
                    command + ' was updated successfully')
            else:
                channelThread.sendMessage(
                    command + ' was not updated successfully. The command '
                    'might not exist')
        return True
    elif action in ['del', 'delete', 'rem', 'remove',]:
        with database.factory.getDatabase() as db:
            result = db.deleteCustomCommand(
                channelThread.channel[1:], level, command)
            if result:
                channelThread.sendMessage(
                    command + ' was removed successfully')
            else:
                channelThread.sendMessage(
                    command + ' was not removed successfully. The command '
                    'might not exist')
        return True
    
    return False

def parseCommandMessageInput(message):
    allowPermissions = {
        None: '',
        '': '',
        'any': '',
        'all': '',
        'public': '',
        'moderator': 'moderator',
        'mod': 'moderator',
        'broadcaster': 'broadcaster',
        'streamer': 'broadcaster',
        'admin': 'admin',
        'twitchadmin': 'admin',
        'staff': 'staff',
        'twitchstaff': 'staff',
        'owner': 'owner',
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
        
        return (action.lower(), level, command, fullText)
    except Exception:
        return None