﻿from ...api import twitch
from ...database import factory
from ..library import timeout
from ..library.chat import feature, not_permission, permission
from bot import config, utils
import datetime
import http.client
import json
import re
import threading
import urllib.error
import urllib.parse
import urllib.request

twitchUrlRegex = (r"(?:https?:\/\/)?(?:[-a-zA-Z0-9@:%_\+~#=]+\.)+[a-z]{2,6}\b"
                  r"(?:[-a-zA-Z0-9@:%_\+.~#?&//=]*)")
#twitchUrlRegex = r"(?:game:(?:[-a-zA-Z0-9@:%_\+.~#?&//=]*))|" + twitchUrlRegex

# This is for banning the users who post a URL with no follows
@feature('nourlredirect')
@not_permission('moderator')
@permission('chatModerator')
def filterNoUrlForBots(args):
    match = re.search(twitchUrlRegex, str(args.message))
    if match is not None:
        params = args.chat, args.nick, args.message, args.timestamp
        threading.Thread(target=checkIfUrlMaybeBad, args=params).start()
    return False

def checkIfUrlMaybeBad(chat, nick, message, timestamp):
    try:
        uri = '/kraken/users/' + nick + '/follows/channels?limit=1'
        response, data = twitch.twitchCall(None, 'GET', uri)
        followerData = json.loads(data.decode('utf-8'))
        if int(followerData['_total']) > 0:
            return False
    except Exception:
        return
    
    # Record all urls with users of no follows
    utils.logIrcMessage(chat.ircChannel + '#blockurl.log',
                       '{nick}: {message}'.format(nick=nick, message=message),
                       timestamp)

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
                utils.logIrcMessage(
                    chat.ircChannel + '#blockurl-match.log',
                    '{nick}: {original} -> {response}'.format(
                        nick=nick, original=originalUrl, response=responseUrl),
                    timestamp)
                with factory.getDatabase() as database:
                    timeout.timeoutUser(
                        database, chat, nick, 'redirectUrl', 1, message)
                return
        except urllib.error.HTTPError as e:
            parsedOriginal = urllib.parse.urlparse(url)
            responseUrl = e.geturl()
            parsedReponse = urllib.parse.urlparse(responseUrl)
            if parsedOriginal.netloc != parsedReponse.netloc:
                utils.logIrcMessage(
                    chat.ircChannel + '#blockurl-match.log',
                    '{nick}: {original} -> {response}'.format(
                        nick=nick, original=originalUrl, response=responseUrl),
                    timestamp)
                with factory.getDatabase() as database:
                    timeout.timeoutUser(
                        database, chat, nick, 'redirectUrl', 1, message)
                return
        except urllib.error.URLError as e:
            try:
                if e.reason.errno not in [-2, 11001]:
                    utils.logException(message, timestamp)
            except BaseException as e:
                utils.logException(message, timestamp)
        except:
            utils.logException(message, timestamp)
