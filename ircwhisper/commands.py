from config import config
import ircwhisper.commandList
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
def parse(tags, nick, message):
    if len(message) == 0:
        return
    
    msgParts = message.split(None)
    if len(msgParts) == 0:
        return
    
    name = nick + '-' + str(msgParts[0]) + '-'
    name += str(time.time())
    params = tags, nick, message, msgParts
    threading.Thread(target=threadParse, args=params, name=name).start()
    
def threadParse(tags, nick, message, msgParts):
    if False: # Hints for Intellisense
        nick = str()
        message = str()
        msgParts = [str(), str()]
    
    try:
        if tags is not None and 'user-type' in tags:
            userType = tags['user-type']
        else:
            userType = ''
        if tags is not None and 'turbo' in tags:
            turbo = tags['turbo']
        else:
            turbo = '0'
        if config.owner is not None:
            isOwner = nick == config.owner.lower()
        else:
            isOwner = False
        isStaff = isOwner or userType in typeStaff
        isAdmin = isStaff or userType in typeAdmin
        isGlobalMod = isAdmin or userType in typeGlobalMod
        isTurbo = isOwner or bool(int(turbo))
        permissions = {
            'owner': isOwner,
            'staff': isStaff,
            'admin': isAdmin,
            'globalMod': isGlobalMod,
            'turbo': isTurbo,
            }
    
        command = str(msgParts[0]).lower()
    
        complete = False
        arguments = nick, message, msgParts, permissions
        if command in ircwhisper.commandList.commands:
            commInfo = ircwhisper.commandList.commands[command]
            hasPerm = True
            if commInfo[1] is not None:
                permissionSet = commInfo[1].split('+')
                for perm in permissionSet:
                    hasPerm = hasPerm and permissions[perm]
            if hasPerm and commInfo[0] is not None:
                complete = commInfo[0](*arguments)
    except:
        extra = 'From: ' + nick + '\nMessage: ' + message
        ircbot.irc.logException(extra)
