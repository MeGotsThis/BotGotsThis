import config
import datetime
import database.factory
import http.client
import ircbot.irc
import ircbot.twitchApi
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
def filterNoUrlForBots(channelData, nick, message, msgParts, permissions):
    with database.factory.getDatabase() as db:
        if not db.hasFeature(channelData.channel[1:], 'nourlredirect'):
            return False
    
    if permissions['moderator']:
        return False
    match = re.search(twitchUrlRegex, message)
    if match is not None:
        params = channelData, nick, message
        threading.Thread(target=checkIfUrlMaybeBad, args=params).start()
    return False

def checkIfUrlMaybeBad(channelData, nick, message):
    try:
        uri = '/kraken/users/' + nick + '/follows/channels?limit=1'
        response, data = ircbot.twitchApi.twitchCall(None, 'GET', uri)
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
                    'User-Agent': 'MeGotsThis/' + config.config.botnick,
                    })
            urlRequest = urllib.request.urlopen(request)
            parsedOriginal = urllib.parse.urlparse(url)
            parsedReponse = urllib.parse.urlparse(urlRequest.geturl())
            if parsedOriginal.netloc != parsedReponse.netloc:
                channelData.sendMessage('.ban ' + nick)
                return
        except (urllib.error.URLError, urllib.error.HTTPError,
                http.client.InvalidURL):
            ircbot.irc.logException(message)
        except:
            ircbot.irc.logException(message)
