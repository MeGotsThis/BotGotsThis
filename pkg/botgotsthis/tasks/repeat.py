from datetime import datetime
from typing import Tuple, cast  # noqa: F401

import bot
from bot import data  # noqa: F401
from lib import database
from lib.helper import timeout


async def autoRepeatMessage(timestamp: datetime) -> None:
    db: database.Database
    async with database.get_database() as db:
        database_: database.DatabaseMain = cast(database.DatabaseMain, db)
        row: Tuple[str, str, str]
        async for row in database_.getAutoRepeatToSend():
            broadcaster: str
            name: str
            message: str
            broadcaster, name, message = row
            if broadcaster in bot.globals.channels:
                await database_.sentAutoRepeat(broadcaster, name)
                channel: data.Channel = bot.globals.channels[broadcaster]
                channel.send(message)
                if channel.isMod:
                    await timeout.record_timeout(channel, None, message, None,
                                                 'autorepeat')
