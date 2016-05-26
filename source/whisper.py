from .database.factory import getDatabase
from bot import config, utils
from bot.data.argument import WhisperCommandArgs
from bot.data.message import Message
from bot.data.permissions import WhisperPermissionSet
from lists import whisper
import datetime
import sys
import threading
import time
import traceback

# Set up our commands function
def parse(tags, nick, rawMessage, timestamp):
    if len(rawMessage) == 0:
        return
    
    message = Message(rawMessage)
    if len(message) == 0:
        return
    
    name = '{nick}-{command}-{time}'.format(
        nick=nick, command=message.command, time=time.time())
    params = tags, nick, message, timestamp
    threading.Thread(target=threadParse, args=params, name=name).start()
    
def threadParse(tags, nick, message, timestamp):
    if False: # Hints for Intellisense
        nick = str()
        message = Message('')
    
    try:
        permissions = WhisperPermissionSet(tags, nick)
    
        complete = False
        with getDatabase() as database:
            arguments = WhisperCommandArgs(database, nick, message,
                                           permissions, timestamp)
            if message.command in whisper.commands:
                commInfo = whisper.commands[message.command]
                hasPerm = True
                if commInfo[1] is not None:
                    permissionSet = commInfo[1].split('+')
                    for perm in permissionSet:
                        hasPerm = hasPerm and permissions[perm]
                if hasPerm and commInfo[0] is not None:
                    complete = commInfo[0](arguments)
    except:
        extra = 'From: {nick}\nMessage: {message}'.format(
            nick=nick, message=message)
        utils.logException(extra, timestamp)
