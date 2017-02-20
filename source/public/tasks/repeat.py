import bot.globals
from bot import data
from datetime import datetime
from ..library import timeout
from ...database import DatabaseBase, factory


def autoRepeatMessage(timestamp: datetime) -> None:
    database: DatabaseBase
    with factory.getDatabase() as database:
        for broadcaster, name, message in list(database.getAutoRepeatToSend()):
            if broadcaster in bot.globals.channels:
                database.sentAutoRepeat(broadcaster, name)
                channel: data.Channel = bot.globals.channels[broadcaster]
                channel.send(message)
                if channel.isMod:
                    timeout.record_timeout(database, channel, None, message,
                                           None, 'autorepeat')
