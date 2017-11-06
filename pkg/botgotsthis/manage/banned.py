from typing import Iterable, List, Optional  # noqa: F401

import bot
from bot import utils
from lib import database as databaseM
from lib.data import ManageBotArgs, Send
from lib.database import DatabaseMain  # noqa: F401
from lib.helper import message

needReason: List[str] = ['add', 'insert', 'del', 'delete', 'rem', 'remove',
                         'remove']


async def manageBanned(args: ManageBotArgs) -> bool:
    if len(args.message) < 3:
        return False
    if args.message.lower[2] in ['list']:
        return await list_banned_channels(args.send)

    if len(args.message) < 5:
        if args.message.lower[2] in needReason:
            args.send(args.nick + ' -> Reason needs to be specified')
            return True
        return False
    channel: str = args.message.lower[3]
    if args.message.lower[2] in ['add', 'insert']:
        return await insert_banned_channel(channel, args.message[4:],
                                           args.nick, args.send)
    if args.message.lower[2] in ['del', 'delete', 'rem', 'remove']:
        return await delete_banned_channel(channel, args.message[4:],
                                           args.nick, args.send)
    return False


async def list_banned_channels(send: Send) -> bool:
    bannedChannels: Iterable[str]
    db: DatabaseMain
    async with databaseM.get_main_database() as db:
        bannedChannels = [channel async for channel
                          in db.listBannedChannels()]
    if bannedChannels:
        send(message.messagesFromItems(bannedChannels, 'Banned Channels: '))
    else:
        send('There are no banned channels')
    return True


async def insert_banned_channel(channel: str,
                                reason: str,
                                nick: str,
                                send: Send) -> bool:
    if channel == bot.config.botnick:
        send('Cannot ban the bot itself')
        return True
    result: bool
    db: DatabaseMain
    async with databaseM.get_main_database() as db:
        bannedWithReason: Optional[str]
        bannedWithReason = await db.isChannelBannedReason(channel)
        if bannedWithReason is not None:
            send(f'{channel} is already banned for: {bannedWithReason}')
            return True
        result = await db.addBannedChannel(channel, reason, nick)
        if result:
            db.discardAutoJoin(channel)
            utils.partChannel(channel)

    msg: str
    if result:
        msg = f'Chat {channel} is now banned'
    else:
        msg = f'Chat {channel} could not be banned. Error has occured.'
    send(msg)
    return True


async def delete_banned_channel(channel: str,
                                reason: str,
                                nick: str,
                                send: Send) -> bool:
    result: bool
    db: DatabaseMain
    async with databaseM.get_main_database() as db:
        bannedWithReason: Optional[str]
        bannedWithReason = await db.isChannelBannedReason(channel)
        if bannedWithReason is None:
            send(f'{channel} is not banned')
            return True
        result = await db.removeBannedChannel(channel, reason, nick)

    msg: str
    if result:
        msg = f'Chat {channel} is now unbanned'
    else:
        msg = f'Chat {channel} could not be unbanned. Error has occured.'
    send(msg)
    return True
