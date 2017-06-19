import bot.globals

from datetime import datetime
from typing import cast

from bot import data
from ..library import timeout
from ... import database


async def autoRepeatMessage(timestamp: datetime) -> None:
    db: database.Database
    async with await database.get_database() as db:
        database_: database.DatabaseMain = cast(database.DatabaseMain, db)
        for broadcaster, name, message in list(database_.getAutoRepeatToSend()):
            if broadcaster in bot.globals.channels:
                database_.sentAutoRepeat(broadcaster, name)
                channel: data.Channel = bot.globals.channels[broadcaster]
                channel.send(message)
                if channel.isMod:
                    await timeout.record_timeout(channel, None, message, None,
                                                 'autorepeat')
