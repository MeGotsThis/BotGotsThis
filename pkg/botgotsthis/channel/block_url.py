import asyncio
import re

import aiohttp

import bot


from datetime import datetime
from urllib.parse import ParseResult, urlparse  # noqa: F401
from typing import Match, cast  # noqa: F401

from bot import data, utils  # noqa: F401
from source.api import twitch
from source.data import ChatCommandArgs
from source.data.message import Message
from source import database
from ..library import timeout
from ..library.chat import feature, permission


twitchUrlRegex: str = (
    # r"(?:game:(?:[-a-zA-Z0-9@:%_\+.~#?&//=]*))|"
    r"(?:https?:\/\/)?(?:[-a-zA-Z0-9@:%_\+~#=]+\.)+[a-z]{2,6}\b"
    r"(?:[-a-zA-Z0-9@:%_\+.~#?&//=]*)")


# This is for banning the users who post a URL with no follows
@feature('nourlredirect')
@permission('bannable')
@permission('chatModerator')
async def filterNoUrlForBots(args: ChatCommandArgs) -> bool:
    if re.search(twitchUrlRegex, str(args.message)):
        asyncio.ensure_future(
            check_domain_redirect(
                args.chat, args.nick, args.message, args.timestamp))
    return False


async def check_domain_redirect(chat: 'data.Channel',
                                nick: str,
                                message: Message,
                                timestamp: datetime) -> None:
    if await twitch.num_followers(nick):
        return

    # Record all urls with users of no follows
    utils.logIrcMessage(f'{chat.ircChannel}#blockurl.log',
                        f'{nick}: {message}',
                        timestamp)

    session: aiohttp.ClientSession
    async with aiohttp.ClientSession() as session:
        match: Match[str]
        for match in re.finditer(twitchUrlRegex, str(message)):
            originalUrl: str = match.group(0)
            url: str = originalUrl
            if (not url.startswith('http://')
                    and not url.startswith('https://')):
                url = 'http://' + url
            headers = {'User-Agent': 'BotGotsThis/' + bot.config.botnick}
            try:
                response: aiohttp.ClientSession
                async with session.get(url, headers=headers) as response:
                    isBadRedirect: bool = compare_domains(
                        url, str(response.url), chat=chat, nick=nick,
                        timestamp=timestamp)
                    if isBadRedirect:
                        await handle_different_domains(chat, nick, message)
                        return
            except aiohttp.ClientConnectorError:
                pass
            except:
                utils.logException(str(message), timestamp)


def compare_domains(originalUrl: str,
                    responseUrl: str, *,
                    chat: 'data.Channel',
                    nick: str,
                    timestamp: datetime) -> bool:
    parsedOriginal: ParseResult = urlparse(originalUrl)
    parsedResponse: ParseResult = urlparse(responseUrl)
    original: str = parsedOriginal.netloc
    response: str = parsedResponse.netloc
    if original.startswith('www.'):
        original = original[len('www.'):]
    if response.startswith('www.'):
        response = response[len('www.'):]
    if original != response:
        utils.logIrcMessage(f'{chat.ircChannel}#blockurl-match.log',
                            f'{nick}: {originalUrl} -> {responseUrl}',
                            timestamp)
        return True
    return False


async def handle_different_domains(chat: 'data.Channel',
                                   nick: str,
                                   message: Message) -> None:
    db: database.Database
    async with database.get_database() as db:
        database_: database.DatabaseMain
        database_ = cast(database.DatabaseMain, db)
        await timeout.timeout_user(database_, chat, nick, 'redirectUrl', 1,
                                   str(message), 'Blocked Redirected URL')
