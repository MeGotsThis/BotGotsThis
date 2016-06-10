from ...api import twitch
from ...data.argument import ChatCommandArgs
from ...data.message import Message
from ...database import factory
from ..library import timeout
from ..library.chat import feature, not_permission, permission
from bot import config, utils
from bot.data import channel
from datetime import datetime
from typing import Tuple
import http.client
import re
import threading
import urllib.error
import urllib.parse
import urllib.request

twitchUrlRegex = (#r"(?:game:(?:[-a-zA-Z0-9@:%_\+.~#?&//=]*))|"
                  r"(?:https?:\/\/)?(?:[-a-zA-Z0-9@:%_\+~#=]+\.)+[a-z]{2,6}\b"
                  r"(?:[-a-zA-Z0-9@:%_\+.~#?&//=]*)")


# This is for banning the users who post a URL with no follows
@feature('nourlredirect')
@not_permission('moderator')
@permission('chatModerator')
def filterNoUrlForBots(args: ChatCommandArgs) -> bool:
    if re.search(twitchUrlRegex, str(args.message)):
        params = args.chat, args.nick, args.message, args.timestamp  # type: Tuple['channel.Channel', str, Message, datetime]
        threading.Thread(target=checkIfUrlMaybeBad, args=params).start()
    return False


def checkIfUrlMaybeBad(chat: 'channel.Channel',
                       nick: str,
                       message: Message,
                       timestamp: datetime):
    if not twitch.getFollowerCount(nick):
        return
    
    # Record all urls with users of no follows
    utils.logIrcMessage(chat.ircChannel + '#blockurl.log',
                        '{nick}: {message}'.format(nick=nick, message=message),
                        timestamp)

    for match in re.finditer(twitchUrlRegex, str(message)):  # --typing: Match[str]
        originalUrl = match.group(0)  # type: str
        url = originalUrl  # type: str
        if not url.startswith('http://') and not url.startswith('https://'):
            url = 'http://' + url
        try:
            request = urllib.request.Request(
                url, headers={
                    'User-Agent': 'MeGotsThis/' + config.botnick,
                    })  # type: urllib.request.Request
            with urllib.request.urlopen(request) as urlRequest:  # --type: http.client.HTTPResponse
                if not isinstance(urlRequest, http.client.HTTPResponse):
                    raise TypeError()
                parsedOriginal = urllib.parse.urlparse(url)  # type: urllib.parse.ParseResult
                responseUrl = urlRequest.geturl()  # type: str
                parsedReponse = urllib.parse.urlparse(responseUrl)  # type: urllib.parse.ParseResult
                if parsedOriginal.netloc != parsedReponse.netloc:
                    utils.logIrcMessage(
                        chat.ircChannel + '#blockurl-match.log',
                        '{nick}: {original} -> {response}'.format(
                            nick=nick, original=originalUrl,
                            response=responseUrl),
                        timestamp)
                    with factory.getDatabase() as database:
                        timeout.timeoutUser(
                            database, chat, nick, 'redirectUrl', 1, str(message))
                    return
        except urllib.error.HTTPError as e:
            parsedOriginal = urllib.parse.urlparse(url)
            responseUrl = e.geturl()  # type: ignore
            parsedReponse = urllib.parse.urlparse(responseUrl)
            if parsedOriginal.netloc != parsedReponse.netloc:
                utils.logIrcMessage(
                    chat.ircChannel + '#blockurl-match.log',
                    '{nick}: {original} -> {response}'.format(
                        nick=nick, original=originalUrl, response=responseUrl),
                    timestamp)
                with factory.getDatabase() as database:
                    timeout.timeoutUser(
                        database, chat, nick, 'redirectUrl', 1, str(message))
                return
        except urllib.error.URLError as e:
            try:
                if e.reason.errno not in [-2, 11001]:  # type: ignore
                    utils.logException(str(message), timestamp)
            except BaseException:
                utils.logException(str(message), timestamp)
        except:
            utils.logException(str(message), timestamp)
