from .database.factory import getDatabase
from .params.permissions import WhisperPermissionSet
from bot import config, utils
from lists import whisper
import datetime
import sys
import threading
import time
import traceback

# Set up our commands function
def parse(tags, nick, message, now):
    if len(message) == 0:
        return
    
    tokens = message.split(None)
    if len(tokens) == 0:
        return
    
    name = nick + '-' + str(tokens[0]) + '-'
    name += str(time.time())
    params = tags, nick, message, tokens, now
    threading.Thread(target=threadParse, args=params, name=name).start()
    
def threadParse(tags, nick, message, tokens, now):
    if False: # Hints for Intellisense
        nick = str()
        message = str()
        tokens = [str(), str()]
    
    try:
        permissions = WhisperPermissionSet(tags, nick)
        command = str(tokens[0]).lower()
    
        complete = False
        with getDatabase() as db:
            arguments = db, nick, message, tokens, permissions, now
            if command in whisper.commands:
                commInfo = whisper.commands[command]
                hasPerm = True
                if commInfo[1] is not None:
                    permissionSet = commInfo[1].split('+')
                    for perm in permissionSet:
                        hasPerm = hasPerm and permissions[perm]
                if hasPerm and commInfo[0] is not None:
                    complete = commInfo[0](*arguments)
    except:
        extra = 'From: ' + nick + '\nMessage: ' + message
        utils.logException(extra, now)
