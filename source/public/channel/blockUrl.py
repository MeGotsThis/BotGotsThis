﻿from ...api import twitch
from bot import config, utils
import datetime
import http.client
import json
import re
import threading
import urllib.error
import urllib.parse
import urllib.request

twitchUrlRegex = r"(?:https?:\/\/)?(?:[-a-zA-Z0-9@:%_\+~#=]+\.)+[a-z]{2,6}\b"
twitchUrlRegex += r"(?:[-a-zA-Z0-9@:%_\+.~#?&//=]*)"
#twitchUrlRegex = r"(?:game:(?:[-a-zA-Z0-9@:%_\+.~#?&//=]*))|" + twitchUrlRegex

# This is for banning the users who post a URL with no follows
def filterNoUrlForBots(db, channel, nick, message, msgParts, permissions):
    if not db.hasFeature(channel.channel, 'nourlredirect'):
        return False
    
    if permissions['moderator']:
        return False
    match = re.search(twitchUrlRegex, message)
    if match is not None:
        params = channel, nick, message
        threading.Thread(target=checkIfUrlMaybeBad, args=params).start()
    return False

def checkIfUrlMaybeBad(channel, nick, message):
    try:
        uri = '/kraken/users/' + nick + '/follows/channels?limit=1'
        response, data = twitch.twitchCall(None, 'GET', uri)
        followerData = json.loads(data.decode('utf-8'))
        if int(followerData['_total']) > 0:
            return False
    except Exception:
        return
    
    matches = re.findall(twitchUrlRegex, message)
    for url in matches:
        if not url.startswith('http://') and not url.startswith('https://'):
            url = 'http://' + url
        try:
            request = urllib.request.Request(
                url, headers={
                    'User-Agent': 'MeGotsThis/' + config.botnick,
                    })
            urlRequest = urllib.request.urlopen(request)
            parsedOriginal = urllib.parse.urlparse(url)
            parsedReponse = urllib.parse.urlparse(urlRequest.geturl())
            if parsedOriginal.netloc != parsedReponse.netloc:
                channel.sendMessage('.ban ' + nick)
                return
        except urllib.error.HTTPError as e:
            parsedOriginal = urllib.parse.urlparse(url)
            parsedReponse = urllib.parse.urlparse(e.geturl())
            if parsedOriginal.netloc != parsedReponse.netloc:
                channel.sendMessage('.ban ' + nick)
                return
        except urllib.error.URLError as e:
            try:
                if e.reason.errno not in [-2, 11001]:
                    utils.logException(message)
            except BaseException as e:
                utils.logException(message)
        except:
            utils.logException(message)