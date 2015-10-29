from ...api import twitch
from bot import globals
import copy
import datetime
import json

def checkStreamsAndChannel(timestamp):
    if not globals.channels:
        return
    channels = copy.copy(globals.channels)
    channelsList = ','.join([c[1:] for c in globals.channels])
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
        uri = '/kraken/channels/' + channel[1:]
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
