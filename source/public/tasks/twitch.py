import copy
import datetime
import ircbot.irc
import ircbot.twitchApi
import json

def checkStreamsAndChannel(timestamp):
    if not ircbot.irc.channels:
        return
    channels = copy.copy(ircbot.irc.channels)
    channelsList = ','.join([c[1:] for c in ircbot.irc.channels])
    uri = '/kraken/streams?channel=' + channelsList
    response, responseData = ircbot.twitchApi.twitchCall(None, 'GET', uri)
    onlineStreams = []
    if response.status == 200:
        streamsData = json.loads(responseData.decode('utf-8'))
        for stream in streamsData['streams']:
            channel = stream['channel']['name'].lower()
            params = stream['created_at'], '%Y-%m-%dT%H:%M:%SZ',
            streamingSince = datetime.datetime.strptime(*params)
            twitchStatus = stream['channel']['status']
            twitchGame = stream['channel']['game']
            channelData = channels['#' + channel]
            channelData.streamingSince = streamingSince
            channelData.twitchStatus = twitchStatus
            channelData.twitchGame = twitchGame
            onlineStreams.append('#' + channel)
    
    for channel in channels:
        if channel in onlineStreams:
            continue
        uri = '/kraken/channels/' + channel[1:]
        response, responseData = ircbot.twitchApi.twitchCall(None, 'GET', uri)
        if response.status != 200:
            continue
        stream = json.loads(responseData.decode('utf-8'))
        twitchStatus = stream['status']
        twitchGame = stream['game']
        channelData = channels[channel]
        channelData.streamingSince = None
        channelData.twitchStatus = twitchStatus
        channelData.twitchGame = twitchGame
