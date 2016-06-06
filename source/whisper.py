import threading
import time
from bot import utils
from lists import whisper
from .data.argument import WhisperCommandArgs
from .data.message import Message
from .data.permissions import WhisperPermissionSet
from .database.factory import getDatabase


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
    threading.Thread(target=whisperCommand, args=params, name=name).start()
    

def whisperCommand(tags, nick, message, timestamp):
    try:
        permissions = WhisperPermissionSet(tags, nick)
    
        complete = False
        with getDatabase() as database:
            arguments = WhisperCommandArgs(database, nick, message,
                                           permissions, timestamp)
            for command in commandsToProcess(message.command):
                if command(arguments):
                    return
    except:
        extra = 'From: {nick}\nMessage: {message}'.format(
            nick=nick, message=message)
        utils.logException(extra, timestamp)


def commandsToProcess(command):
    if command in whisper.commands:
        if whisper.commands[command] is not None:
            yield whisper.commands[command]
