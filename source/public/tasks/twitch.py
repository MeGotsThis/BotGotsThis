from ...api import twitch
from ...database.factory import getDatabase
from bot import globals, utils
from contextlib import suppress
import copy
import datetime
import json
import random
import socket
import threading
import time

def checkStreamsAndChannel(timestamp):
    if not globals.channels:
        return
    with suppress(socket.gaierror):
        channels = copy.copy(globals.channels)
        onlineStreams = twitch.checkOnlineStreams(channels.keys())
        for channel in onlineStreams:
            chat = channels[channel]
            channelData.twitchCache = timestamp
            (channelData.streamingSince, channelData.twitchStatus,
             channelData.twitchGame) = onlineStreams[channel]
        
        for channel in channels:
            if channel in onlineStreams:
                continue
            channels[channel].streamingSince = None

def checkOfflineChannels(timestamp):
    if not globals.channels:
        return
    cacheDuration = datetime.timedelta(seconds=300)
    channels = copy.copy(globals.channels)
    offlineChannels = [c for c, ch in channels.items()
                       if (channels[c].streamingSince is None and
                           timestamp - ch.twitchCache >= cacheDuration)]
    if not offlineChannels:
        return
    channel = random.choice(offlineChannels)
    chat = channels[channel]
    chat.twitchCache, old = timestamp, chat.twitchCache
    try:
        (chat.streamingSince, chat.twitchStatus,
         chat.twitchGame) = twitch.channelStatusAndGame(channel)
    except socket.gaierror:
        chat.twitchCache = old

def checkChatServers(timestamp):
    cooldown = datetime.timedelta(seconds=3600)
    channels = copy.copy(globals.channels)
    toCheck = [c for c, ch in channels.items()
               if (ch.serverCheck is None or
                   timestamp - ch.serverCheck >= cooldown)]
    if not toCheck:
        return
    channel = random.choice(toCheck)
    channels[channel].serverCheck = timestamp
    cluster = twitch.twitchChatServer(channel)
    if (cluster is not None and cluster in globals.clusters and
        globals.clusters[cluster] is not channels[channel].socket):
        with getDatabase() as db:
            priority = db.getAutoJoinsPriority(channel)
            priority = priority if priority is not None else float('inf')
            utils.ensureServer(channel, priority, cluster)
            db.setAutoJoinServer(channel, cluster)
