import threading
import time
from bot import data, utils
from bot.twitchmessage.irctags import IrcMessageTagsReadOnly
from datetime import datetime
from lists import channel as commandList
from typing import Iterator
from .data import argument
from .data.message import Message
from .data.permissions import ChatPermissionSet
from .database import factory


# Set up our commands function
def parse(chat: 'data.Channel',
          tags: IrcMessageTagsReadOnly,
          nick: str,
          rawMessage: str,
          timestamp: datetime) -> None:
    if len(rawMessage) == 0:
        return
    
    message = Message(rawMessage)  # type: Message
    if len(message) == 0:
        return
    
    name = '{channel}-{command}-{time}'.format(
        channel=chat.channel, command=message.command, time=time.time())  # type: str
    params = chat, tags, nick, message, timestamp  # type: tuple
    threading.Thread(target=chatCommand, args=params, name=name).start()
    

def chatCommand(chat: 'data.Channel',
                tags: IrcMessageTagsReadOnly,
                nick: str,
                message: Message,
                timestamp: datetime) -> None:
    try:
        permissions = ChatPermissionSet(tags, nick, chat)  # type: ChatPermissionSet
    
        with factory.getDatabase() as database:
            arguments = argument.ChatCommandArgs(
                database, chat, tags, nick, message, permissions, timestamp)  # type: argument.ChatCommandArgs
            for command in commandsToProcess(message.command):  # --type: argument.ChatCommand
                if command(arguments):
                    return
    except:
        extra = 'Channel: {channel}\nMessage: {message}'.format(
            channel=chat.channel, message=message)
        utils.logException(extra, timestamp)


def commandsToProcess(command: str) -> Iterator[argument.ChatCommand]:
    yield from commandList.filterMessage
    if command in commandList.commands:
        if commandList.commands[command] is not None:
            yield commandList.commands[command]
    for starting in commandList.commandsStartWith:
        if command.startswith(starting):
            if commandList.commandsStartWith[starting] is not None:
                yield commandList.commandsStartWith[starting]
    yield from commandList.processNoCommand
