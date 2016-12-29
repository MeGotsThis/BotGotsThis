import bot.globals
from bot import data
from datetime import datetime
from ..library import timeout
from ...database import DatabaseBase, factory


def autoRepeatMessage(timestamp: datetime) -> None:
    with factory.getDatabase() as database:  # type: DatabaseBase
        for broadcaster, name, message in list(database.getAutoRepeatToSend()):
            if broadcaster in bot.globals.channels:
                database.sentAutoRepeat(broadcaster, name)
                channel = bot.globals.channels[broadcaster]  # type: data.Channel
                channel.send(message)
                if channel.isMod:
                    timeout.record_timeout(database, channel, None, message,
                                           None, 'autorepeat')
