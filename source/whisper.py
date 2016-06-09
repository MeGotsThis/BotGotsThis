import threading
import time
from bot import utils
from bot.twitchmessage.irctags import IrcMessageTagsReadOnly
from datetime import datetime
from lists import whisper
from typing import Iterator
from .data import argument
from .data.message import Message
from .data.permissions import WhisperPermissionSet
from .database.factory import getDatabase


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
        with getDatabase() as database:
            arguments = argument.WhisperCommandArgs(
                database, nick, message, permissions, timestamp)  # type: argument.WhisperCommandArgs
            for command in commandsToProcess(message.command):  # --type: argument.WhisperCommand
                if command(arguments):
                    return
    except:
        extra = 'From: {nick}\nMessage: {message}'.format(
            nick=nick, message=message)
        utils.logException(extra, timestamp)


def commandsToProcess(command: str) -> Iterator[argument.WhisperCommand]:
    if command in whisper.commands:
        if whisper.commands[command] is not None:
            yield whisper.commands[command]
