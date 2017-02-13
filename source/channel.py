﻿import lists.channel
import threading
import time
from bot import data as botData, utils
from bot.twitchmessage import IrcMessageTagsReadOnly
from datetime import datetime
from typing import Iterator, Optional
from . import data
from .data.message import Message
from .data.permissions import ChatPermissionSet
from .database import factory


# Set up our commands function
def parse(chat: 'botData.Channel',
          tags: [IrcMessageTagsReadOnly],
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
    

def chatCommand(chat: 'botData.Channel',
                tags: Optional[IrcMessageTagsReadOnly],
                nick: str,
                message: Message,
                timestamp: datetime) -> None:
    try:
        if tags is not None:
            if 'room-id' in tags:
                utils.saveTwitchId(chat.channel, str(tags['room-id']), timestamp)
            if 'user-id' in tags:
                utils.saveTwitchId(nick, str(tags['user-id']), timestamp)
        with factory.getDatabase() as database:
            permitted = database.isPermittedUser(chat.channel, nick)  # type: bool
            manager = database.isBotManager(nick)  # type: bool
            permissions = ChatPermissionSet(tags, nick, chat, permitted, manager)  # type: ChatPermissionSet

            arguments = data.ChatCommandArgs(
                database, chat, tags, nick, message, permissions,
                timestamp)  # type: data.ChatCommandArgs
            for command in commandsToProcess(message.command):  # type: argument.ChatCommand
                if command(arguments):
                    return
    except:
        extra = 'Channel: {channel}\nMessage: {message}'.format(
            channel=chat.channel, message=message)
        utils.logException(extra, timestamp)


def commandsToProcess(command: str) -> Iterator[data.ChatCommand]:
    yield from lists.channel.filterMessage
    if command in lists.channel.commands:
        if lists.channel.commands[command] is not None:
            yield lists.channel.commands[command]
    for starting in lists.channel.commandsStartWith:
        if command.startswith(starting):
            if lists.channel.commandsStartWith[starting] is not None:
                yield lists.channel.commandsStartWith[starting]
    yield from lists.channel.processNoCommand
