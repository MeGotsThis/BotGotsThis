from ...api import twitch
from ..common import broadcaster, send
import datetime
import email.utils
import json
import time

def commandHello(db, chat, tags, nick, message, msgParts, permissions, now):
    chat.sendMessage('Hello Kappa')
    return True

def commandCome(db, chat, tags, nick, message, msgParts, permissions, now):
    broadcaster.botCome(db, nick, send.channel(chat))
    return True

def commandLeave(db, chat, tags, nick, message, msgParts, permissions, now):
    return broadcaster.botLeave(chat.channel, send.channel(chat))

def commandEmpty(db, chat, tags, nick, message, msgParts, permissions, now):
    broadcaster.botEmpty(chat.channel, send.channel(chat))
    return True

def commandAutoJoin(db, chat, tags, nick, message, msgParts, permissions, now):
    broadcaster.botAutoJoin(db, nick, send.channel(chat), msgParts)
    return True

def commandSetTimeoutLevel(db, chat, tags, nick, message, msgParts,
                           permissions, now):
    broadcaster.botSetTimeoutLevel(db, chat.channel, send.channel(chat),
                                   msgParts)
    return True

def commandUptime(db, chat, tags, nick, message, msgParts, permissions, now):
    currentTime = datetime.datetime.utcnow()
    if 'uptime' in chat.sessionData:
        since = currentTime - chat.sessionData['uptime']
        if since < datetime.timedelta(seconds=60):
            return False
    chat.sessionData['uptime'] = currentTime

    if not chat.isStreaming:
        msg = chat.channel + ' is currently not streaming or has not '
        msg += 'been for a minute'
        chat.sendMessage(msg)
        return True

    response, data = twitch.twitchCall(
        chat.channel, 'GET', '/kraken/',
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
                
            msg = 'Uptime: ' + str(currentTime - chat.streamingSince)
            chat.sendMessage(msg)
            return True
        raise ValueError()
    except (ValueError, KeyError) as e:
        msg = 'Fail to get information from Twitch.tv'
        chat.sendMessage(msg)
    except:
        msg = 'Unknown Error'
        chat.sendMessage(msg)
