from .database.factory import getDatabase
from .params.message import Message
from .params.permissions import WhisperPermissionSet
from bot import config, utils
from lists import whisper
import datetime
import sys
import threading
import time
import traceback

# Set up our commands function
def parse(tags, nick, rawMessage, now):
    if len(rawMessage) == 0:
        return
    
    message = Message(rawMessage)
    if len(message) == 0:
        return
    
    name = nick + '-' + str(tokens[0]) + '-'
    name += str(time.time())
    params = tags, nick, message, now
    threading.Thread(target=threadParse, args=params, name=name).start()
    
def threadParse(tags, nick, message, now):
    if False: # Hints for Intellisense
        nick = str()
        message = str()
    
    try:
        permissions = WhisperPermissionSet(tags, nick)
    
        complete = False
        with getDatabase() as db:
            arguments = db, nick, message, permissions, now
            if message.command in whisper.commands:
                commInfo = whisper.commands[message.command]
                hasPerm = True
                if commInfo[1] is not None:
                    permissionSet = commInfo[1].split('+')
                    for perm in permissionSet:
                        hasPerm = hasPerm and permissions[perm]
                if hasPerm and commInfo[0] is not None:
                    complete = commInfo[0](*arguments)
    except:
        extra = 'From: ' + nick + '\nMessage: ' + str(message)
        utils.logException(extra, now)
