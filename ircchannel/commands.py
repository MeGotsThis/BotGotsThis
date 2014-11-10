from config import config
import ircchannel.commandList
import ircchannel.text
import ircbot.irc
import datetime

# Set up our commands function
def parse(channelThread, nick, message):
    if len(message) == 0 or message[0] != '!':
        return
    
    msgParts = message.split(None)
    
    if config.owner is not None:
        isOwner = nick == config.owner.lower()
        _ = channelThread.channel == '#' + config.botnick
        isOwnerChan = channelThread.channel == '#' + config.owner or _
    else:
        isOwner = False
        isOwnerChan = False
    isBroadcaster = '#' + nick == channelThread.channel
    isMod = isBroadcaster or isOwner
    isMod = isMod or nick in channelThread.mods
    isChanMod = config.botnick in channelThread.mods
    permissions = {
        'owner': isOwner,
        'ownerChan': isOwnerChan,
        'broadcaster': isOwner,
        'moderator': isMod,
        'channelModerator': isChanMod,
        }
    
    command = msgParts[0].lower()
    
    complete = False
    arguments = channelThread, nick, message, msgParts, permissions
    if command in ircchannel.commandList.commands:
        commandInfo = ircchannel.commandList.commands[command]
        hasPermission = True
        if commandInfo[1] is not None:
            permissionSet = commandInfo[1].split('+')
            for perm in permissionSet:
                hasPermission = hasPermission and permissions[perm]
        if hasPermission:
            complete = commandInfo[0](*arguments)
    if not complete:
        for comm in ircchannel.commandList.commandsStartWith:
            if command.startswith(comm):
                commandInfo = ircchannel.commandList.commandsStartWith[comm]
                hasPermission = True
                if commandInfo[1] is not None:
                    permissionSet = commandInfo[1].split('+')
                    for perm in permissionSet:
                        hasPermission = hasPermission and permissions[perm]
                if hasPermission:
                    complete = commandInfo[0](*arguments)
    if not complete:
        ircchannel.text.customCommands(*arguments)
