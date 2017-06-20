import bot.config
from bot import utils
from typing import Iterable, List, Optional
from ..library import message
from ...data import ManageBotArgs, Send
from ...database import DatabaseMain

needReason: List[str] = ['add', 'insert', 'del', 'delete', 'rem', 'remove',
                         'remove']


async def manageBanned(args: ManageBotArgs) -> bool:
    if len(args.message) < 3:
        return False
    if args.message.lower[2] in ['list']:
        return await list_banned_channels(args.database, args.send)
    
    if len(args.message) < 5:
        if args.message.lower[2] in needReason:
            args.send(args.nick + ' -> Reason needs to be specified')
            return True
        return False
    channel: str = args.message.lower[3]
    if args.message.lower[2] in ['add', 'insert']:
        return await insert_banned_channel(channel, args.message[4:],
                                           args.nick, args.database, args.send)
    if args.message.lower[2] in ['del', 'delete', 'rem', 'remove']:
        return await delete_banned_channel(channel, args.message[4:],
                                           args.nick, args.database, args.send)
    return False


async def list_banned_channels(database: DatabaseMain,
                         send: Send) -> bool:
    bannedChannels: Iterable[str]
    bannedChannels = [channel async for channel
                      in database.listBannedChannels()]
    if bannedChannels:
        send(message.messagesFromItems(bannedChannels, 'Banned Channels: '))
    else:
        send('There are no banned channels')
    return True


async def insert_banned_channel(channel: str,
                                reason: str,
                                nick: str,
                                database: DatabaseMain,
                                send: Send) -> bool:
    if channel == bot.config.botnick:
        send('Cannot ban the bot itself')
        return True
    bannedWithReason: Optional[str]
    bannedWithReason = await database.isChannelBannedReason(channel)
    if bannedWithReason is not None:
        send('{channel} is already banned for: {reason}'.format(
            channel=channel, reason=bannedWithReason))
        return True
    result: bool = await database.addBannedChannel(channel, reason, nick)
    if result:
        database.discardAutoJoin(channel)
        utils.partChannel(channel)

    msg: str
    if result:
        msg = 'Chat {channel} is now banned'
    else:
        msg = 'Chat {channel} could not be banned. Error has occured.'
    send(msg.format(channel=channel))
    return True


async def delete_banned_channel(channel: str,
                                reason: str,
                                nick: str,
                                database: DatabaseMain,
                                send: Send) -> bool:
    bannedWithReason: Optional[str]
    bannedWithReason = await database.isChannelBannedReason(channel)
    if bannedWithReason is None:
        send('{channel} is not banned'.format(channel=channel))
        return True
    result: bool = await database.removeBannedChannel(channel, reason, nick)

    msg: str
    if result:
        msg = 'Chat {channel} is now unbanned'
    else:
        msg = 'Chat {channel} could not be unbanned. Error has occured.'
    send(msg.format(channel=channel))
    return True
