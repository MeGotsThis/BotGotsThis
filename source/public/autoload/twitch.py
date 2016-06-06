from ..tasks import twitch
from bot.globals import background
import datetime
import threading

threading.Timer(1, background.addTask, 
                (twitch.checkStreamsAndChannel,
                 datetime.timedelta(seconds=30))).start()
threading.Timer(10, background.addTask,
                (twitch.checkOfflineChannels,
                 datetime.timedelta(seconds=0.05))).start()
threading.Timer(10, background.addTask,
                (twitch.checkChatServers,
                 datetime.timedelta(seconds=0.05))).start()
