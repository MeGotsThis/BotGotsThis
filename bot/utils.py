from bot import config
from .channel import Channel
from .globals import channels, clusters
import datetime
import os.path
import sys
import threading
import traceback

def joinChannel(channel, priority=float('inf'), cluster='aws'):
    if cluster is None or cluster not in clusters:
        return False
    channel = channel.lower()
    if channel in channels:
        t = min(channels[channel].joinPriority, priority)
        channels[channel].joinPriority = t
        return False
    channels[channel] = Channel(channel, clusters[cluster], priority)
    clusters[cluster].joinChannel(channels[channel])
    return True

def partChannel(channel):
    if channel in channels:
        channels[channel].part()
        del channels[channel]

ENSURE_CLUSTER_UNKNOWN = int(-3)
ENSURE_CLUSTER_NONE = int(-2)
ENSURE_REJOIN = int(-1)
ENSURE_CORRECT = int(0)
ENSURE_NOT_JOINED = int(1)

def ensureServer(channel, priority=float('inf'), cluster='aws'):
    if channel not in channels:
        return ENSURE_NOT_JOINED
    if cluster is None:
        return ENSURE_CLUSTER_NONE
    if cluster not in clusters:
        partChannel(channel)
        return ENSURE_CLUSTER_UNKNOWN
    if clusters[cluster] is channels[channel].socket:
        channels[channel].joinPriority = min(
            channels[channel].joinPriority, priority)
        return ENSURE_CORRECT
    partChannel(channel)
    joinChannel(channel, priority, cluster)
    return ENSURE_REJOIN

def logIrcMessage(filename, message, timestamp=None):
    if config.ircLogFolder is None:
        return
    logDateFormat = '%Y-%m-%dT%H:%M:%S.%f '
    timestamp = datetime.datetime.utcnow() if timestamp is None else timestamp
    timestampStr = timestamp.strftime(logDateFormat)
    fullfilename = os.path.join(config.ircLogFolder, filename)
    with open(fullfilename, 'a', encoding='utf-8') as file:
        file.write(timestampStr + message + '\n')

def logException(extraMessage=None, now=None):
    if config.exceptionLog is None:
        return
    if now is None:
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
