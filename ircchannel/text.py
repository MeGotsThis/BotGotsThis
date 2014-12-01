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
    
    action = msgParts[1]
    if action == 'add':
        if msgParts[2].startswith('level='):
            commandMessage = msgParts.split(None, 4)[4]
        else:
            commandMessage = msgParts.split(None, 3)[3]
    elif action == 'edit':
        if msgParts[2].startswith('level='):
            commandMessage = msgParts.split(None, 4)[4]
        else:
            commandMessage = msgParts.split(None, 3)[3]
    elif action in ['del', 'delete', 'rem', 'remove',]:
        pass
    
    return False

def parseCommandMessageInput(message):
    msgParts = message.split()
    action = msgParts[1]
    
    return (action, )