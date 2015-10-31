from ...api import twitch
from ..common import broadcaster, send
import datetime
import email.utils
import json
import time

def commandHello(db, channel, nick, message, msgParts, permissions):
    channel.sendMessage('Hello Kappa')
    return True

def commandCome(db, channel, nick, message, msgParts, permissions):
    broadcaster.botCome(db, nick, send.channel(channel))
    return True

def commandLeave(db, channel, nick, message, msgParts, permissions):
    return broadcaster.botLeave(channel.channel, send.channel(channel))

def commandEmpty(db, channel, nick, message, msgParts, permissions):
    broadcaster.botEmpty(channel.channel, send.channel(channel))
    return True

def commandAutoJoin(db, channel, nick, message, msgParts, permissions):
    broadcaster.botAutoJoin(db, nick, send.channel(channel), msgParts)
    return True

def commandUptime(db, channel, nick, message, msgParts, permissions):
    currentTime = datetime.datetime.utcnow()
    if 'uptime' in channel.sessionData:
        since = currentTime - channel.sessionData['uptime']
        if since < datetime.timedelta(seconds=60):
            return False
    channel.sessionData['uptime'] = currentTime

    if not channel.isStreaming:
        msg = channel.channel + ' is currently not streaming or has not '
        msg += 'been for a minute'
        channel.sendMessage(msg)
        return True

    response, data = twitch.twitchCall(
        channel.channel, 'GET', '/kraken/',
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
                
            msg = 'Uptime: ' + str(currentTime - channel.streamingSince)
            channel.sendMessage(msg)
            return True
        raise ValueError()
    except (ValueError, KeyError) as e:
        msg = 'Fail to get information from Twitch.tv'
        channel.sendMessage(msg)
    except:
        msg = 'Unknown Error'
        channel.sendMessage(msg)
