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
