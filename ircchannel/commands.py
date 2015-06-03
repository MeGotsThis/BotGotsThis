from config import config
import ircchannel.commandList
import ircbot.channeldata
import ircchannel.text
import ircuser.jtv
import ircbot.irc
import threading
import traceback
import datetime
import time
import sys

typeStaff = ['staff']
typeAdmin = ['staff', 'admin']
typeGlobalMod = ['staff', 'admin', 'global_mod']
typeMod = ['staff', 'admin', 'global_mod', 'mod']

# Set up our commands function
def parse(channelData, tags, nick, message):
    if len(message) == 0:
        return
    
    if nick == 'jtv':
        ircuser.jtv.parse(channelData, message)
        return
    
    msgParts = message.split(None)
    if len(msgParts) == 0:
        return
    
    name = channelData.channel + '-' + str(msgParts[0]) + '-'
    name += str(time.time())
    params = channelData, tags, nick, message, msgParts
    threading.Thread(target=threadParse, args=params, name=name).start()
    
def threadParse(channelData, tags, nick, message, msgParts):
    if False: # Hints for Intellisense
        channelData = ircbot.channeldata.ChannelData('', None)
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
            subscriber = ''
        if tags is not None and 'turbo' in tags:
            turbo = tags['turbo']
        else:
            turbo = ''
        if config.owner is not None:
            isOwner = nick == config.owner.lower()
            _ = channelData.channel == '#' + config.botnick
            isOwnerChan = channelData.channel == '#' + config.owner or _
        else:
            isOwner = False
            isOwnerChan = False
        isStaff = isOwner or userType in typeStaff
        isAdmin = isStaff or userType in typeAdmin
        isGlobalMod = isAdmin or userType in typeGlobalMod
        isBroadcaster = nick == channelData.channel[1:]
        isBroadcaster = isGlobalMod or isAdmin or isBroadcaster
        isMod = isBroadcaster or userType in typeMod
        isSubscriber = isBroadcaster or bool(int(subscriber))
        isTurbo = isBroadcaster or bool(int(turbo))
        isChanMod = channelData.isMod
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
            commInfo = ircchannel.commandList.commands[command]
            hasPerm = True
            if commInfo[1] is not None:
                permissionSet = commInfo[1].split('+')
                for perm in permissionSet:
                    hasPerm = hasPerm and permissions[perm]
            if hasPerm and commInfo[0] is not None:
                complete = commInfo[0](*arguments)
        if not complete:
            for comm in ircchannel.commandList.commandsStartWith:
                if command.startswith(comm):
                    commInfo = ircchannel.commandList.commandsStartWith[comm]
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
            ircchannel.text.customCommands(*arguments)
    except Exception as e:
        now = datetime.datetime.now()
        _ = traceback.format_exception(*sys.exc_info())
        if config.exceptionLog is not None:
            with open(config.exceptionLog, 'a', encoding='utf-8') as file:
                file.write(now.strftime('%Y-%m-%d %H:%M:%S.%f '))
                file.write('Exception in thread ')
                file.write(threading.current_thread().name + ':\n')
                file.write('Channel: ' + channelData.channel + '\n')
                file.write('Message: ' + message + '\n')
                file.write('Nick: ' + nick + '\n')
                file.write(''.join(_))
