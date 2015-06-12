# Import some necessary libraries.
from config import config
import database.factory
import ircbot.irc
import threading
import traceback
import datetime
import sys
import time

print(str(datetime.datetime.utcnow()) + ' Starting')
ircbot.irc.mainChat.start()
ircbot.irc.eventChat.start()
ircbot.irc.groupChat.start()
ircbot.irc.messaging.start()
ircbot.irc.join.start()

try:
    ircbot.irc.joinChannel(config.botnick, float('-inf'), ircbot.irc.mainChat)
    if config.owner:
        ircbot.irc.joinChannel(config.owner, float('-inf'),
                               ircbot.irc.mainChat)
    with database.factory.getDatabase() as db:
        for channelRow in db.getAutoJoinsChats():
            params = channelRow['broadcaster'], channelRow['priority'],
            if channelRow['eventServer']:
                params += ircbot.irc.eventChat,
            else:
                params += ircbot.irc.mainChat,
            ircbot.irc.joinChannel(*params)
    
    ircbot.irc.messaging.join()
except:
    ircbot.irc.logException()
    raise
finally:
    print(str(datetime.datetime.utcnow()) + ' Ended')
