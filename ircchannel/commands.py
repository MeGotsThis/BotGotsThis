from config import config
import ircchannel.commandList
import ircchannel.text
import ircuser.jtv
import ircbot.irc
import datetime

# Set up our commands function
def parse(channelData, nick, message):
    if len(message) == 0:
        return
    
    if nick == 'jtv':
        ircuser.jtv.parse(channelData, message)
    
    msgParts = message.split(None)
    if len(msgParts) == 0:
        return
    
    if config.owner is not None:
        isOwner = nick == config.owner.lower()
        _ = channelData.channel == '#' + config.botnick
        isOwnerChan = channelData.channel == '#' + config.owner or _
    else:
        isOwner = False
        isOwnerChan = False
    isStaff = isOwner or nick in channelData.twitchStaff
    isAdmin = isStaff or nick in channelData.twitchAdmin
    isBroadcaster = isStaff or isAdmin or '#' + nick == channelData.channel
    isMod = isBroadcaster or nick in channelData.mods
    isSubscriber = isBroadcaster or nick in channelData.subscribers
    isTurbo = isBroadcaster or nick in channelData.turboUsers
    isChanMod = config.botnick in channelData.mods
    permissions = {
        'owner': isOwner,
        'ownerChan': isOwnerChan,
        'staff': isStaff,
        'admin': isAdmin,
        'broadcaster': isBroadcaster,
        'moderator': isMod,
        'subscriber': isMod,
        'turbo': isMod,
        'channelModerator': isChanMod,
        }
    
    command = msgParts[0].lower()
    
    complete = False
    arguments = channelData, nick, message, msgParts, permissions
    if command in ircchannel.commandList.commands:
        commandInfo = ircchannel.commandList.commands[command]
        hasPermission = True
        if commandInfo[1] is not None:
            permissionSet = commandInfo[1].split('+')
            for perm in permissionSet:
                hasPermission = hasPermission and permissions[perm]
        if hasPermission and commandInfo[0] is not None:
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
                if hasPermission and commandInfo[0] is not None:
                    complete = commandInfo[0](*arguments)
    if not complete:
        ircchannel.text.customCommands(*arguments)
