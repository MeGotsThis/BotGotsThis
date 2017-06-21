import asyncio

import lists.channel

from datetime import datetime
from typing import Iterator, Optional, cast

from bot import data as botData, utils
from bot.twitchmessage import IrcMessageTagsReadOnly
from .data.message import Message
from .data.permissions import ChatPermissionSet
from . import data
from . import database


# Set up our commands function
def parse(chat: 'botData.Channel',
          tags: Optional[IrcMessageTagsReadOnly],
          nick: str,
          rawMessage: str,
          timestamp: datetime) -> None:
    if len(rawMessage) == 0:
        return
    
    message: Message = Message(rawMessage)
    if len(message) == 0:
        return
    
    asyncio.ensure_future(chatCommand(chat, tags, nick, message, timestamp))

async def chatCommand(chat: 'botData.Channel',
                      tags: Optional[IrcMessageTagsReadOnly],
                      nick: str,
                      message: Message,
                      timestamp: datetime) -> None:
    permitted: bool
    manager: bool
    permissions: ChatPermissionSet
    arguments: data.ChatCommandArgs
    command: data.ChatCommand
    db: database.Database
    try:
        if tags is not None:
            if 'room-id' in tags:
                utils.saveTwitchId(chat.channel, str(tags['room-id']), timestamp)
            if 'user-id' in tags:
                utils.saveTwitchId(nick, str(tags['user-id']), timestamp)
        async with await database.get_database() as db:
            databaseObj: database.DatabaseMain
            databaseObj = cast(database.DatabaseMain, db)
            permitted = await databaseObj.isPermittedUser(chat.channel, nick)
            manager = await databaseObj.isBotManager(nick)
            permissions = ChatPermissionSet(tags, nick, chat, permitted,
                                            manager)

            arguments = data.ChatCommandArgs(
                databaseObj, chat, tags, nick, message, permissions,
                timestamp)
            for command in commandsToProcess(message.command):
                if await command(arguments):
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
