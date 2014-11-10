from . import textOwner
from . import textMods
from . import textPublic
import ircbot.irc

def customCommands(channelThread, nick, message, msgParts, permissions):
    command = msgParts[0]
    channel = channelThread.channel
    if permissions['owner']:
        owner = textOwner.owner
        if channel in owner and command in owner[channel]:
            channelThread.sendMessage(
                               owner[channel][command].replace('\n', ''))
            return True
        if command in owner['global']:
            channelThread.sendMessage(
                               owner['global'][command].replace('\n', ''))
            return True
    if permissions['moderator']:
        mods = textMods.mods
        if channel in mods and command in mods[channel]:
            channelThread.sendMessage(
                               mods[channel][command].replace('\n', ''))
            return True
        if command in mods['global']:
            channelThread.sendMessage(
                               mods['global'][command].replace('\n', ''))
            return True
    public = textPublic.public
    if channel in public and command in public[channel]:
        channelThread.sendMessage(public[channel][command].replace('\n', ''))
        return True
    if command in public['global']:
        channelThread.sendMessage(public['global'][command].replace('\n', ''))
        return True
    return False

