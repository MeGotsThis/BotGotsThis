from .channel import Channel
from .globals import channels, mainChat
import datetime

def joinChannel(channel, priority=float('inf'), server=mainChat):
    channel = channel.lower()
    if channel in channels:
        t = min(channels[channel].joinPriority, priority)
        channels[channel].joinPriority = t
        return False
    channels[channel] = Channel(channel, server, priority)
    server.joinChannel(channels[channel])
    return True

def partChannel(channel):
    if channel in channels:
        channels[channel].part()
        del channels[channel]

ENSURE_REJOIN_TO_MAIN = int(-2)
ENSURE_REJOIN_TO_EVENT = int(-1)
ENSURE_CORRECT = int(0)
ENSURE_NOT_JOINED = int(1)

def ensureServer(channel, priority=float('inf'), server=mainChat):
    if channel not in channels:
        return ENSURE_NOT_JOINED
    if server is channels[channel].socket:
        channels[channel].joinPriority = min(
            channels[channel].joinPriority, priority)
        return ENSURE_CORRECT
    partChannel(channel)
    joinChannel(channel, priority, server)
    if server is eventChat:
        return ENSURE_REJOIN_TO_EVENT
    else:
        return ENSURE_REJOIN_TO_MAIN

def logException(extraMessage=None):
    if config.exceptionLog is None:
        return
    now = datetime.datetime.utcnow()
    logDateFormat = '%Y-%m-%dT%H:%M:%S.%f '
    _ = traceback.format_exception(*sys.exc_info())
    with open(config.exceptionLog, 'a', encoding='utf-8') as file:
        file.write(now.strftime(logDateFormat))
        file.write('Exception in thread ')
        file.write(threading.current_thread().name + ':\n')
        if extraMessage:
            file.write(extraMessage + '\n')
        file.write(''.join(_))
