import asyncio
from datetime import datetime
from typing import Iterator, Mapping, Optional, cast  # noqa: F401

import lib.items.channel
from bot import data as botData, utils  # noqa: F401
from bot.twitchmessage import IrcMessageTagsReadOnly
from . import data
from . import cache
from . import database
from .data.message import Message
from .data.permissions import ChatPermissionSet


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
    cacheStore: cache.CacheStore
    db: database.Database
    try:
        if tags is not None:
            if 'room-id' in tags:
                utils.saveTwitchId(chat.channel, str(tags['room-id']),
                                   timestamp)
            if 'user-id' in tags:
                utils.saveTwitchId(nick, str(tags['user-id']), timestamp)
        async with cache.get_cache() as cacheStore, \
                database.get_database() as db:
            databaseObj: database.DatabaseMain
            databaseObj = cast(database.DatabaseMain, db)
            permitted = await databaseObj.isPermittedUser(chat.channel, nick)
            manager = await cacheStore.isBotManager(nick)
            permissions = ChatPermissionSet(tags, nick, chat, permitted,
                                            manager)

            arguments = data.ChatCommandArgs(
                cacheStore, databaseObj, chat, tags, nick, message,
                permissions, timestamp)
            for command in commandsToProcess(message.command):
                if await command(arguments):
                    return
    except Exception:
        utils.logException(f'Channel: {chat.channel}\nMessage: {message}',
                           timestamp)


def commandsToProcess(command: str) -> Iterator[data.ChatCommand]:
    yield from lib.items.channel.filterMessage()
    commands: Mapping[str, Optional[data.ChatCommand]]
    commands = lib.items.channel.commands()
    if command in commands:
        if commands[command] is not None:
            yield commands[command]
    commands = lib.items.channel.commandsStartWith()
    starting: str
    for starting in commands:
        if command.startswith(starting):
            if commands[starting] is not None:
                yield commands[starting]
    yield from lib.items.channel.processNoCommand()
