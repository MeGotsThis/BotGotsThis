# Import some necessary libraries.
from config import config
import ircbot.irc
import traceback
import datetime
import sys
import time

print('Starting')
ircbot.irc.messaging.start()

try:
    for channel in config.autoJoin:
        ircbot.irc.joinChannel(channel)
    
    ircbot.irc.messaging.join()
except:
    ircbot.irc.messaging.running = False
    now = datetime.datetime.now()
    exc_type, exc_value, exc_traceback = sys.exc_info()
    traceback.print_exception(exc_type, exc_value, exc_traceback)
    _ = traceback.format_exception(exc_type, exc_value, exc_traceback)
    if config.exceptionLog is not None:
        with open(config.exceptionLog, 'a', encoding='utf-8') as file:
            file.write(now.strftime('%Y-%m-%d %H:%M:%S.%f '))
            file.write(' ' + ''.join(_))
    raise
finally:
    print('Ended')