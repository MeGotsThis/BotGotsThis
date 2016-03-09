from ..tasks import twitch
from bot.thread import background
import datetime

background.addTask(twitch.checkStreamsAndChannel,
                   datetime.timedelta(seconds=30))
background.addTask(twitch.checkChatServers,
                   datetime.timedelta(seconds=0.05))
