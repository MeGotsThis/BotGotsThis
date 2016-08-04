import lists.whisper
import threading
import time
from bot import utils
from bot.twitchmessage import IrcMessageTagsReadOnly
from datetime import datetime
from typing import Iterator
from . import data
from .data.message import Message
from .data.permissions import WhisperPermissionSet
from .database import factory


# Set up our commands function
def parse(tags: IrcMessageTagsReadOnly,
          nick: str,
          rawMessage: str,
          timestamp: datetime):
    if len(rawMessage) == 0:
        return
    
    message = Message(rawMessage)
    if len(message) == 0:
        return
    
    name = '{nick}-{command}-{time}'.format(
        nick=nick, command=message.command, time=time.time())  # type: str
    params = tags, nick, message, timestamp  # type: tuple
    threading.Thread(target=whisperCommand, args=params, name=name).start()
    

def whisperCommand(tags: IrcMessageTagsReadOnly,
                   nick: str,
                   message: Message,
                   timestamp: datetime) -> None:
    try:
        permissions = WhisperPermissionSet(tags, nick)  # type: WhisperPermissionSet

        complete = False
        with factory.getDatabase() as database:
            arguments = data.WhisperCommandArgs(
                database, nick, message, permissions, timestamp)  # type: data.WhisperCommandArgs
            for command in commandsToProcess(message.command):  # --type: data.WhisperCommand
                if command(arguments):
                    return
    except:
        extra = 'From: {nick}\nMessage: {message}'.format(
            nick=nick, message=message)
        utils.logException(extra, timestamp)


def commandsToProcess(command: str) -> Iterator[data.WhisperCommand]:
    if command in lists.whisper.commands:
        if lists.whisper.commands[command] is not None:
            yield lists.whisper.commands[command]
