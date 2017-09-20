from typing import Optional, Union  # noqa: F401

import bot
from bot import utils
from source.api import twitch
from source.data import Send
from source.database import DatabaseMain
from source.helper import timeout


async def join(database: DatabaseMain,
               channel: str,
               send: Send) -> bool:
    bannedWithReason: Optional[str]
    bannedWithReason = await database.isChannelBannedReason(channel)
    if bannedWithReason is not None:
        send('Chat ' + channel + ' is banned from joining')
        return True
    priority: Union[int, float] = await database.getAutoJoinsPriority(channel)

    cluster: Optional[str] = await twitch.chat_server(channel)
    if cluster not in bot.globals.clusters:
        send('Unknown chat server for ' + channel)
    elif utils.joinChannel(channel, priority, cluster):
        send('Joining ' + channel)
    else:
        result: int = utils.ensureServer(channel, priority, cluster)
        if result == utils.ENSURE_CORRECT:
            send('Already joined ' + channel)
        elif result == utils.ENSURE_REJOIN:
            send('Moved ' + channel + ' to correct chat server')
        else:
            send('Unknown error joining ' + channel)
    return True


def part(channel: str,
         send: Send) -> bool:
    if channel == bot.config.botnick:
        return False
    utils.partChannel(channel)
    send('Leaving ' + channel)
    return True


async def say(nick: str,
              channel: str,
              message: str) -> bool:
    if channel in bot.globals.channels:
        await timeout.record_timeout(bot.globals.channels[channel], nick,
                                     message, None, 'say')
        bot.globals.channels[channel].send(message)
        return True
    return False


def empty_all(send: Send) -> bool:
    utils.clearAllChat()
    send('Cleared all queued messages')
    return True


def empty(channel: str,
          send: Send) -> bool:
    if channel in bot.globals.channels:
        chan = bot.globals.channels[channel]
        chan.clear()
        send('Cleared all queued messages for ' + channel)
        return True
    return False
