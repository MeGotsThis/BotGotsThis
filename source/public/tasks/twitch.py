from ...api import twitch
from ...database.factory import getDatabase
from bot import globals, utils
import copy
import datetime
import json
import random

def checkStreamsAndChannel(timestamp):
    if not globals.channels:
        return
    channels = copy.copy(globals.channels)
    channelsList = ','.join([c for c in globals.channels])
    uri = '/kraken/streams?channel=' + channelsList
    response, responseData = twitch.twitchCall(None, 'GET', uri)
    onlineStreams = []
    if response.status == 200:
        streamsData = json.loads(responseData.decode('utf-8'))
        for stream in streamsData['streams']:
            channel = stream['channel']['name'].lower()
            params = stream['created_at'], '%Y-%m-%dT%H:%M:%SZ',
            streamingSince = datetime.datetime.strptime(*params)
            twitchStatus = stream['channel']['status']
            twitchGame = stream['channel']['game']
            channelData = channels[channel]
            channelData.streamingSince = streamingSince
            channelData.twitchStatus = twitchStatus
            channelData.twitchGame = twitchGame
            onlineStreams.append(channel)
    
    for channel in channels:
        if channel in onlineStreams:
            continue
        uri = '/kraken/channels/' + channel
        response, responseData = twitch.twitchCall(None, 'GET', uri)
        if response.status != 200:
            continue
        stream = json.loads(responseData.decode('utf-8'))
        twitchStatus = stream['status']
        twitchGame = stream['game']
        channelData = channels[channel]
        channelData.streamingSince = None
        channelData.twitchStatus = twitchStatus
        channelData.twitchGame = twitchGame

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
    if (cluster is not None and
        globals.clusters[cluster] is not channels[channel].socket):
        with getDatabase() as db:
            priority = db.getAutoJoinsPriority(channel)
            priority = priority if priority is not None else float('inf')
            utils.ensureServer(channel, priority, cluster)
            db.setAutoJoinServer(channel, cluster)
