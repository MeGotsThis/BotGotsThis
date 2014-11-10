from . import textOwner
from . import textBroadcaster
from . import textMods
from . import textPublic
import ircbot.irc

def customCommands(channelThread, nick, message, msgParts, permissions):
    command = msgParts[0]
    channel = channelThread.channel
    message = None
    
    public = textPublic.public
    if command in public['global']:
        message = public['global'][command].replace('\n', '')
    if channel in public and command in public[channel]:
        message = public[channel][command].replace('\n', '')
    
    if permissions['moderator']:
        mods = textMods.mods
        if command in mods['global']:
            message = mods['global'][command].replace('\n', '')
        if channel in mods and command in mods[channel]:
            message = mods[channel][command].replace('\n', '')
    
    if permissions['broadcaster']:
        broadcaster = textBroadcaster.broadcaster
        if command in broadcaster['global']:
            message = broadcaster['global'][command].replace('\n', '')
        if channel in broadcaster and command in broadcaster[channel]:
            message = broadcaster[channel][command].replace('\n', '')
    
    if permissions['owner']:
        owner = textOwner.owner
        if command in owner['global']:
            message = owner['global'][command].replace('\n', '')
        if channel in owner and command in owner[channel]:
            message = owner[channel][command].replace('\n', '')
    
    if message:
        channelThread.sendMessage(message)
        return True
    
    return False

