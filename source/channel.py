from .irccommand import jtv
from bot import config, utils
from bot.channel import Channel
from lists import channel
import datetime
import sys
import threading
import time
import traceback

typeStaff = ['staff']
typeAdmin = ['staff', 'admin']
typeGlobalMod = ['staff', 'admin', 'global_mod']
typeMod = ['staff', 'admin', 'global_mod', 'mod']

# Set up our commands function
def parse(channel, tags, nick, message):
    if len(message) == 0:
        return
    
    if nick == 'jtv':
        jtv.parse(channel, message)
        return
    
    msgParts = message.split(None)
    if len(msgParts) == 0:
        return
    
    name = channel.channel + '-' + str(msgParts[0]) + '-'
    name += str(time.time())
    params = channel, tags, nick, message, msgParts
    threading.Thread(target=threadParse, args=params, name=name).start()
    
def threadParse(channel, tags, nick, message, msgParts):
    if False: # Hints for Intellisense
        channel = Channel('', None)
        nick = str()
        message = str()
        msgParts = [str(), str()]
    
    try:
        if tags is not None and 'user-type' in tags:
            userType = tags['user-type']
        else:
            userType = ''
        if tags is not None and 'subscriber' in tags:
            subscriber = tags['subscriber']
        else:
            subscriber = '0'
        if tags is not None and 'turbo' in tags:
            turbo = tags['turbo']
        else:
            turbo = '0'
        if config.owner is not None:
            isOwner = nick == config.owner.lower()
            _ = channel.channel == config.botnick
            isOwnerChan = channel.channel == config.owner or _
        else:
            isOwner = False
            isOwnerChan = False
        isStaff = isOwner or userType in typeStaff
        isAdmin = isStaff or userType in typeAdmin
        isGlobalMod = isAdmin or userType in typeGlobalMod
        isBroadcaster = nick == channel.channel
        isBroadcaster = isGlobalMod or isAdmin or isBroadcaster
        isMod = isBroadcaster or userType in typeMod
        isSubscriber = isBroadcaster or bool(int(subscriber))
        isTurbo = isBroadcaster or bool(int(turbo))
        isChanMod = channel.isMod
        permissions = {
            'owner': isOwner,
            'ownerChan': isOwnerChan,
            'staff': isStaff,
            'admin': isAdmin,
            'globalMod': isGlobalMod,
            'broadcaster': isBroadcaster,
            'moderator': isMod,
            'subscriber': isSubscriber,
            'turbo': isTurbo,
            'channelModerator': isChanMod,
            }
    
        command = str(msgParts[0]).lower()
    
        complete = False
        arguments = channel, nick, message, msgParts, permissions
        for filter in channel.filterMessage:
            complete = filter(*arguments)
            if complete:
                break
        if not complete and command in channel.commands:
            commInfo = channel.commands[command]
            hasPerm = True
            if commInfo[1] is not None:
                permissionSet = commInfo[1].split('+')
                for perm in permissionSet:
                    hasPerm = hasPerm and permissions[perm]
            if hasPerm and commInfo[0] is not None:
                complete = commInfo[0](*arguments)
        if not complete:
            for comm in channel.commandsStartWith:
                if command.startswith(comm):
                    commInfo = channel.commandsStartWith[comm]
                    hasPerm = True
                    if commInfo[1] is not None:
                        permissionSet = commInfo[1].split('+')
                        for perm in permissionSet:
                            hasPerm = hasPerm and permissions[perm]
                    if hasPerm and commInfo[0] is not None:
                        complete = commInfo[0](*arguments)
                        if complete:
                            break
        if not complete:
            for process in channel.processNoCommand:
                complete = process(*arguments)
                if complete:
                    break
    except:
        extra = 'Channel: ' + channel.channel + '\nMessage: ' + message
        utils.logException(extra)
