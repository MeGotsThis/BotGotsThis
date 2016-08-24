from ..tasks import twitch
from bot.globals import background
import datetime
import threading


def call_streams(timestamp: datetime.datetime) -> None:
    twitch.checkStreamsAndChannel(timestamp)


def call_offline(timestamp: datetime.datetime) -> None:
    twitch.checkOfflineChannels(timestamp)


def call_server(timestamp: datetime.datetime) -> None:
    twitch.checkChatServers(timestamp)


threading.Timer(1, background.addTask, 
                [call_streams, datetime.timedelta(seconds=30)]).start()
threading.Timer(10, background.addTask,
                [call_offline, datetime.timedelta(seconds=0.05)]).start()
threading.Timer(10, background.addTask,
                [call_server, datetime.timedelta(seconds=0.05)]).start()
