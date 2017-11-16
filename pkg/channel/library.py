import asyncio
import bot
from bot import utils
from typing import List, Optional, Union  # noqa: F401
from lib.data import Send
from lib.data.message import Message
from lib.database import DatabaseMain


async def come(channel: str,
               send: Send) -> bool:
    bannedWithReason: Optional[str]
    priority: Union[float, int]
    db: DatabaseMain
    async with DatabaseMain.acquire() as db:
        bannedWithReason = await db.isChannelBannedReason(channel)
        if bannedWithReason is not None:
            send(f'Chat {channel} is banned from joining')
            return True
        priority = await db.getAutoJoinsPriority(channel)
    joinResult: bool = utils.joinChannel(channel, priority)
    if joinResult:
        send(f'Joining {channel}')
    else:
        send(f'I am already in {channel}')
    return True


async def leave(channel: str,
                send: Send) -> bool:
    if channel == bot.config.botnick:
        return False
    send(f'Bye {channel}')
    await asyncio.sleep(1.0)
    utils.partChannel(channel)
    return True


async def auto_join(channel: str,
                    send: Send,
                    message: Message) -> bool:
    db: DatabaseMain
    async with DatabaseMain.acquire() as db:
        bannedWithReason: Optional[str]
        bannedWithReason = await db.isChannelBannedReason(channel)
        if bannedWithReason is not None:
            send(f'Chat {channel} is banned from joining')
            return True

        if len(message) >= 2:
            removeMsgs: List[str] = ['0', 'false', 'no', 'remove', 'rem',
                                     'delete', 'del', 'leave', 'part']
            if message.lower[1] in removeMsgs:
                return await auto_join_delete(db, channel, send)
        return await auto_join_add(db, channel, send)


async def auto_join_add(db: DatabaseMain,
                        channel: str,
                        send: Send) -> bool:
    result: bool = await db.saveAutoJoin(channel, 0)
    priority: Union[int, float] = await db.getAutoJoinsPriority(channel)

    wasInChat: bool = not utils.joinChannel(channel, priority)

    if result and not wasInChat:
        send(f'''\
Auto join for {channel} is now enabled and joined {channel} chat''')
    elif not wasInChat:
        send(f'''\
Auto join for {channel} is already enabled but now joined {channel} chat''')
    else:
        send(f'''\
Auto join for {channel} is already enabled and already in chat''')
    return True


async def auto_join_delete(db: DatabaseMain,
                           channel: str,
                           send: Send) -> bool:
    result: bool = await db.discardAutoJoin(channel)
    if result:
        send(f'Auto join for {channel} is now disabled')
    else:
        send(f'Auto join for {channel} was never enabled')
    return True
