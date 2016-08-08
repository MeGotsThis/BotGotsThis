from ...api import twitch
from ...data import ChatCommandArgs
from ...data.message import Message
from ...database import factory
from ..library import timeout
from ..library.chat import feature, not_permission, permission
from bot import data, utils
from datetime import datetime
from http.client import HTTPResponse
from urllib.parse import ParseResult, urlparse
from typing import Tuple
import bot.config
import re
import socket
import threading
import urllib.error
import urllib.request

twitchUrlRegex = (#r"(?:game:(?:[-a-zA-Z0-9@:%_\+.~#?&//=]*))|"
                  r"(?:https?:\/\/)?(?:[-a-zA-Z0-9@:%_\+~#=]+\.)+[a-z]{2,6}\b"
                  r"(?:[-a-zA-Z0-9@:%_\+.~#?&//=]*)")  # type: str
ThreadParam = Tuple['data.Channel', str, Message, datetime]


# This is for banning the users who post a URL with no follows
@feature('nourlredirect')
@not_permission('moderator')
@permission('chatModerator')
def filterNoUrlForBots(args: ChatCommandArgs) -> bool:
    if re.search(twitchUrlRegex, str(args.message)):
        params = args.chat, args.nick, args.message, args.timestamp  # type: ThreadParam
        threading.Thread(target=check_domain_redirect, args=params).start()
    return False


def check_domain_redirect(chat: 'data.Channel',
                          nick: str,
                          message: Message,
                          timestamp: datetime) -> None:
    if not twitch.num_followers(nick):
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
                    'User-Agent': 'BotGotsThis/' + bot.config.botnick,
                    })  # type: urllib.request.Request
            with urllib.request.urlopen(request) as response:  # HTTPResponse
                if not isinstance(response, HTTPResponse):
                    raise TypeError()
                if compare_domains(url, response.geturl(),
                                   chat=chat, nick=nick, timestamp=timestamp):
                    handle_different_domains(chat, nick, message)
                    return
        except urllib.error.HTTPError as e:
            if compare_domains(url, e.geturl(),  # type: ignore --
                               chat=chat, nick=nick, timestamp=timestamp):
                handle_different_domains(chat, nick, message)
                return
        except urllib.error.URLError as e:
            if (not isinstance(e.reason, OSError)  # type: ignore --
                    or e.reason.errno != socket.EAI_NONAME):  # type: ignore --
                utils.logException(str(message), timestamp)
        except:
            utils.logException(str(message), timestamp)


def compare_domains(originalUrl: str,
                    responseUrl: str, *,
                    chat: 'data.Channel',
                    nick: str,
                    timestamp: datetime) -> bool:
    parsedOriginal = urlparse(originalUrl)  # type: ParseResult
    parsedResponse = urlparse(responseUrl)  # type: ParseResult
    original = parsedOriginal.netloc  # type: str
    response = parsedResponse.netloc  # type: str
    if original.startswith('www.'):
        original = original[len('www.'):]
    if response.startswith('www.'):
        response = response[len('www.'):]
    if original != response:
        utils.logIrcMessage(
            chat.ircChannel + '#blockurl-match.log',
            '{nick}: {original} -> {response}'.format(
                nick=nick, original=originalUrl, response=responseUrl),
            timestamp)
        return True
    return False


def handle_different_domains(chat: 'data.Channel',
                             nick: str,
                             message: Message) -> None:
    with factory.getDatabase() as database:
        timeout.timeout_user(database, chat, nick, 'redirectUrl', 1,
                             str(message))
