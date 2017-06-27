﻿import asyncio

import lists.whisper

from datetime import datetime
from typing import Iterator, Mapping, Optional, cast  # noqa: F401

from bot import utils
from bot.twitchmessage import IrcMessageTagsReadOnly
from .data.message import Message
from .data.permissions import WhisperPermissionSet
from . import database
from . import data


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

    asyncio.ensure_future(whisperCommand(tags, nick, message, timestamp))


async def whisperCommand(tags: IrcMessageTagsReadOnly,
                         nick: str,
                         message: Message,
                         timestamp: datetime) -> None:
    manager: bool
    permissions: WhisperPermissionSet
    arguments: data.WhisperCommandArgs
    command: data.WhisperCommand
    db: database.Database
    try:
        async with database.get_database() as db:
            databaseObj: database.DatabaseMain
            databaseObj = cast(database.DatabaseMain, db)
            manager = await databaseObj.isBotManager(nick)
            permissions = WhisperPermissionSet(tags, nick, manager)

            arguments = data.WhisperCommandArgs(databaseObj, nick, message,
                                                permissions, timestamp)
            for command in commandsToProcess(message.command):
                if await command(arguments):
                    return
    except:
        extra = 'From: {nick}\nMessage: {message}'.format(
            nick=nick, message=message)
        utils.logException(extra, timestamp)


def commandsToProcess(command: str) -> Iterator[data.WhisperCommand]:
    commands: Mapping[str, Optional[data.WhisperCommand]]
    commands = lists.whisper.commands()
    if command in commands:
        if commands[command] is not None:
            yield commands[command]
    commands = lists.whisper.commandsStartWith()
    starting: str
    for starting in commands:
        if command.startswith(starting):
            if commands[starting] is not None:
                yield commands[starting]
