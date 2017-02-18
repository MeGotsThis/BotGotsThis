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
    
    message: Message = Message(rawMessage)
    if len(message) == 0:
        return
    
    name: str = '{nick}-{command}-{time}'.format(
        nick=nick, command=message.command, time=time.time())
    params: tuple
    params = tags, nick, message, timestamp
    threading.Thread(target=whisperCommand, args=params, name=name).start()
    

def whisperCommand(tags: IrcMessageTagsReadOnly,
                   nick: str,
                   message: Message,
                   timestamp: datetime) -> None:
    manager: bool
    permissions: WhisperPermissionSet
    arguments: data.WhisperCommandArgs
    command: data.WhisperCommand
    try:
        with factory.getDatabase() as database:
            manager = database.isBotManager(nick)
            permissions = WhisperPermissionSet(tags, nick, manager)

            arguments = data.WhisperCommandArgs(database, nick, message,
                                                permissions, timestamp)
            for command in commandsToProcess(message.command):
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
