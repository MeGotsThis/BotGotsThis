from ...api import twitch
from ..common import timeout
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
def filterNoUrlForBots(db, chat, tags, nick, message, msgParts, permissions,
                       now):
    if not permissions['channelModerator']:
        return False
    if not db.hasFeature(chat.channel, 'nourlredirect'):
        return False
    
    if permissions['moderator']:
        return False
    match = re.search(twitchUrlRegex, message)
    if match is not None:
        params = db, chat, nick, message, now
        threading.Thread(target=checkIfUrlMaybeBad, args=params).start()
    return False

def checkIfUrlMaybeBad(db, chat, nick, message, now):
    try:
        uri = '/kraken/users/' + nick + '/follows/channels?limit=1'
        response, data = twitch.twitchCall(None, 'GET', uri)
        followerData = json.loads(data.decode('utf-8'))
        if int(followerData['_total']) > 0:
            return False
    except Exception:
        return
    
    # Record all urls with users of no follows
    log = nick + ': ' + message
    utils.logIrcMessage(chat.ircChannel + '#blockurl.log', log, now)

    matches = re.findall(twitchUrlRegex, message)
    for originalUrl in matches:
        url = originalUrl
        if not url.startswith('http://') and not url.startswith('https://'):
            url = 'http://' + url
        try:
            request = urllib.request.Request(
                url, headers={
                    'User-Agent': 'MeGotsThis/' + config.botnick,
                    })
            urlRequest = urllib.request.urlopen(request)
            parsedOriginal = urllib.parse.urlparse(url)
            responseUrl = urlRequest.geturl()
            parsedReponse = urllib.parse.urlparse(responseUrl)
            if parsedOriginal.netloc != parsedReponse.netloc:
                log = nick + ': ' + originalUrl + ' -> ' + responseUrl
                utils.logIrcMessage(chat.ircChannel + '#blockurl-match.log',
                                    log, now)
                timeout.timeoutUser(db, chat, nick, 'redirectUrl', 1,
                                    message)
                return
        except urllib.error.HTTPError as e:
            parsedOriginal = urllib.parse.urlparse(url)
            responseUrl = e.geturl()
            parsedReponse = urllib.parse.urlparse(responseUrl)
            if parsedOriginal.netloc != parsedReponse.netloc:
                log = nick + ': ' + originalUrl + ' -> ' + responseUrl
                utils.logIrcMessage(chat.ircChannel + '#blockurl-match.log',
                                    log, now)
                timeout.timeoutUser(db, chat, nick, 'redirectUrl', 1,
                                    message)
                return
        except urllib.error.URLError as e:
            try:
                if e.reason.errno not in [-2, 11001]:
                    utils.logException(message, now)
            except BaseException as e:
                utils.logException(message, now)
        except:
            utils.logException(message, now)
