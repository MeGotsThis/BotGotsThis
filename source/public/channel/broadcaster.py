from ...api import twitch
from ..library import broadcaster, send
import datetime
import email.utils
import json
import time

def commandHello(args):
    args.chat.sendMessage('Hello Kappa')
    return True

def commandCome(args):
    broadcaster.botCome(args.database, args.nick, send.channel(args.chat))
    return True

def commandLeave(args):
    return broadcaster.botLeave(args.chat.channel, send.channel(args.chat))

def commandEmpty(args):
    broadcaster.botEmpty(args.chat.channel, send.channel(args.chat))
    return True

def commandAutoJoin(args):
    broadcaster.botAutoJoin(args.database, args.nick, send.channel(args.chat),
                            args.message)
    return True

def commandSetTimeoutLevel(args):
    broadcaster.botSetTimeoutLevel(args.database, args.chat.channel,
                                   send.channel(args.chat), args.message)
    return True

def commandUptime(args):
    currentTime = datetime.datetime.utcnow()
    if 'uptime' in args.chat.sessionData:
        since = currentTime - args.chat.sessionData['uptime']
        if since < datetime.timedelta(seconds=60):
            return False
    args.chat.sessionData['uptime'] = currentTime

    if not args.chat.isStreaming:
        args.chat.sendMessage(
            '{channel} is currently not streaming or has not been for a '
            'minute'.format(channel=args.chat.channel))
        return True

    response, data = twitch.twitchCall(
        args.chat.channel, 'GET', '/kraken/',
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
                
            args.chat.sendMessage(
                'Uptime: {uptime}'.format(
                    uptime=currentTime - args.chat.streamingSince))
            return True
        raise ValueError()
    except (ValueError, KeyError) as e:
        args.chat.sendMessage('Fail to get information from Twitch.tv')
    except:
        args.chat.sendMessage('Unknown Error')
