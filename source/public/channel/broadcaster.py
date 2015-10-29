from ...api import twitch
from ..common import broadcaster
import datetime
import email.utils
import json
import time

def commandHello(channelData, nick, message, msgParts, permissions):
    channelData.sendMessage('Hello Kappa')
    return True

def commandCome(channelData, nick, message, msgParts, permissions):
    broadcaster.botCome(nick, channelData.sendMessage)
    return True

def commandLeave(channelData, nick, message, msgParts, permissions):
    return broadcaster.botLeave(channelData.channel, channelData.sendMessage)

def commandEmpty(channelData, nick, message, msgParts, permissions):
    broadcaster.botEmpty(channelData.channel,
                                     channelData.sendMessage)
    return True

def commandAutoJoin(channelData, nick, message, msgParts, permissions):
    broadcaster.botAutoJoin(nick, channelData.sendMessage, msgParts)
    return True

def commandUptime(channelData, nick, message, msgParts, permissions):
    currentTime = datetime.datetime.utcnow()
    if 'uptime' in channelData.sessionData:
        since = currentTime - channelData.sessionData['uptime']
        if since < datetime.timedelta(seconds=60):
            return False
    channelData.sessionData['uptime'] = currentTime

    if not channelData.isStreaming:
        msg = channelData.channel + ' is currently not streaming or has not '
        msg += 'been for a minute'
        channelData.sendMessage(msg)
        return True

    response, data = twitch.twitchCall(
        channelData.channel, 'GET', '/kraken/',
        headers = {
            'Accept': 'application/vnd.twitchtv.v3+json',
            })
    try:
        if response.status == 200:
            streamData = json.loads(data.decode('utf-8'))
            date = response.getheader('Date')
            dateStruct = email.utils.parsedate(date)
            unixTimestamp = time.mktime(dateStruct)
            currentTime = datetime.datetime.fromtimestamp(unixTimestamp)
                
            msg = 'Uptime: ' + str(currentTime - channelData.streamingSince)
            channelData.sendMessage(msg)
            return True
        raise ValueError()
    except (ValueError, KeyError) as e:
        msg = 'Fail to get information from Twitch.tv'
        channelData.sendMessage(msg)
    except:
        msg = 'Unknown Error'
        channelData.sendMessage(msg)
