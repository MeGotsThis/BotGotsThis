from .database import factory
from .data.argument import ChatCommandArgs
from .data.message import Message
from .data.permissions import ChatPermissionSet
from bot import config, utils
from bot.channel import Channel
from lists import channel as commandList
import datetime
import sys
import threading
import time
import traceback

# Set up our commands function
def parse(chat, tags, nick, rawMessage, timestamp):
    if len(rawMessage) == 0:
        return
    
    message = Message(rawMessage)
    if len(message) == 0:
        return
    
    name = '{channel}-{command}-{time}'.format(
        channel=chat.channel, command=message.command, time=time.time())
    params = chat, tags, nick, message, timestamp
    threading.Thread(target=threadParse, args=params, name=name).start()
    
def threadParse(chat, tags, nick, message, timestamp):
    if False: # Hints for Intellisense
        chat = Channel('', None)
        nick = str()
        message = Message('')
    
    try:
        permissions = ChatPermissionSet(tags, nick, chat)
    
        complete = False
        with factory.getDatabase() as database:
            arguments = ChatCommandArgs(database, chat, tags, nick, message,
                                        permissions, timestamp)
            for filter in commandList.filterMessage:
                complete = filter(arguments)
                if complete:
                    break
            if not complete and message.command in commandList.commands:
                commInfo = commandList.commands[message.command]
                hasPerm = True
                if commInfo[1] is not None:
                    permissionSet = commInfo[1].split('+')
                    for perm in permissionSet:
                        hasPerm = hasPerm and permissions[perm]
                if hasPerm and commInfo[0] is not None:
                    complete = commInfo[0](arguments)
            if not complete:
                for comm in commandList.commandsStartWith:
                    if message.command.startswith(comm):
                        commInfo = commandList.commandsStartWith[comm]
                        hasPerm = True
                        if commInfo[1] is not None:
                            permissionSet = commInfo[1].split('+')
                            for perm in permissionSet:
                                hasPerm = hasPerm and permissions[perm]
                        if hasPerm and commInfo[0] is not None:
                            complete = commInfo[0](arguments)
                            if complete:
                                break
            if not complete:
                for process in commandList.processNoCommand:
                    complete = process(arguments)
                    if complete:
                        break
    except:
        extra = 'Channel: {channel}\nMessage: {message}'.format(
            channel=chat.channel, message=message)
        utils.logException(extra, timestamp)
