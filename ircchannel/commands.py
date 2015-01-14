from config import config
import ircchannel.commandList
import ircbot.channeldata
import ircchannel.text
import ircuser.jtv
import ircbot.irc
import threading
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
    
    name = channelData.channel + '-' + str(msgParts[0]) + '-'
    name += str(time.time())
    params = channelData, nick, message, msgParts
    threading.Thread(target=threadParse, args=params, name=name).start()
    
def threadParse(channelData, nick, message, msgParts):
    if False: # Hints for Intellisense
        channelData = ircbot.channeldata.ChannelData('', None)
        nick = str()
        message = str()
        msgParts = [str(), str()]

    if config.owner is not None:
        isOwner = nick == config.owner.lower()
        _ = channelData.channel == '#' + config.botnick
        isOwnerChan = channelData.channel == '#' + config.owner or _
    else:
        isOwner = False
        isOwnerChan = False
    isStaff = isOwner or nick in channelData.twitchStaff
    isAdmin = isStaff or nick in channelData.twitchAdmin
    isGlobalMod = isAdmin or nick in channelData.globalMods
    isBroadcaster = isGlobalMod or isAdmin or '#' + nick == channelData.channel
    isMod = isBroadcaster or nick in channelData.mods
    isSubscriber = isBroadcaster or nick in channelData.subscribers
    isTurbo = isBroadcaster or nick in channelData.turboUsers
    isChanMod = config.botnick in channelData.mods
    permissions = {
        'owner': isOwner,
        'ownerChan': isOwnerChan,
        'staff': isStaff,
        'admin': isAdmin,
        'globalMod': isGlobalMod,
        'broadcaster': isBroadcaster,
        'moderator': isMod,
        'subscriber': isMod,
        'turbo': isMod,
        'channelModerator': isChanMod,
        }
    
    command = str(msgParts[0]).lower()
    
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
