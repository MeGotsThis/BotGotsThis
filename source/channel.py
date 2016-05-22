from .database import factory
from .params.permissions import ChatPermissionSet
from bot import config, utils
from bot.channel import Channel
from lists import channel as commandList
import datetime
import sys
import threading
import time
import traceback

# Set up our commands function
def parse(chat, tags, nick, message, now):
    if len(message) == 0:
        return
    
    msgParts = message.split(None)
    if len(msgParts) == 0:
        return
    
    name = chat.channel + '-' + str(msgParts[0]) + '-'
    name += str(time.time())
    params = chat, tags, nick, message, msgParts, now
    threading.Thread(target=threadParse, args=params, name=name).start()
    
def threadParse(chat, tags, nick, message, msgParts, now):
    if False: # Hints for Intellisense
        chat = Channel('', None)
        nick = str()
        message = str()
        msgParts = [str(), str()]
    
    try:
        permissions = ChatPermissionSet(tags, nick, chat)
        command = str(msgParts[0]).lower()
    
        complete = False
        with factory.getDatabase() as db:
            arguments = db, chat, tags, nick, message, msgParts, permissions,
            arguments += now,
            for filter in commandList.filterMessage:
                complete = filter(*arguments)
                if complete:
                    break
            if not complete and command in commandList.commands:
                commInfo = commandList.commands[command]
                hasPerm = True
                if commInfo[1] is not None:
                    permissionSet = commInfo[1].split('+')
                    for perm in permissionSet:
                        hasPerm = hasPerm and permissions[perm]
                if hasPerm and commInfo[0] is not None:
                    complete = commInfo[0](*arguments)
            if not complete:
                for comm in commandList.commandsStartWith:
                    if command.startswith(comm):
                        commInfo = commandList.commandsStartWith[comm]
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
                for process in commandList.processNoCommand:
                    complete = process(*arguments)
                    if complete:
                        break
    except:
        extra = 'Channel: ' + chat.channel + '\nMessage: ' + message
        utils.logException(extra, now)
