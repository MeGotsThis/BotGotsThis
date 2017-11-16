from typing import Optional, Union  # noqa: F401

import bot
from bot import utils
from lib.data import Send
from lib.database import DatabaseMain
from lib.helper import timeout


async def join(channel: str,
               send: Send) -> bool:
    priority: Union[int, float]
    db: DatabaseMain
    async with DatabaseMain.acquire() as db:
        bannedWithReason: Optional[str]
        bannedWithReason = await db.isChannelBannedReason(channel)
        if bannedWithReason is not None:
            send(f'Chat {channel} is banned from joining')
            return True
        priority = await db.getAutoJoinsPriority(channel)

    if utils.joinChannel(channel, priority):
        send(f'Joining {channel}')
    else:
        send(f'Already joined {channel}')
    return True


def part(channel: str,
         send: Send) -> bool:
    if channel == bot.config.botnick:
        return False
    utils.partChannel(channel)
    send(f'Leaving {channel}')
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
        bot.globals.channels[channel].clear()
        send(f'Cleared all queued messages for {channel}')
        return True
    return False
