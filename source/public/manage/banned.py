import bot.config
from bot import utils
from typing import Iterable, List, Optional
from ..library import message
from ...data import ManageBotArgs, Send
from ...database import DatabaseBase

needReason = ['add', 'insert', 'del', 'delete', 'rem', 'remove', 'remove']  # type: List[str]


def manageBanned(args: ManageBotArgs) -> bool:
    if len(args.message) < 3:
        return False
    if args.message.lower[2] in ['list']:
        return list_banned_channels(args.database, args.send)
    
    if len(args.message) < 5:
        if args.message.lower[2] in needReason:
            args.send(args.nick + ' -> Reason needs to be specified')
            return True
        return False
    channel = args.message.lower[3]  # type: str
    if args.message.lower[2] in ['add', 'insert']:
        return insert_banned_channel(channel, args.message[4:], args.nick,
                                     args.database, args.send)
    if args.message.lower[2] in ['del', 'delete', 'rem', 'remove']:
        return delete_banned_channel(channel, args.message[4:], args.nick,
                                     args.database, args.send)
    return False


def list_banned_channels(database: DatabaseBase,
                         send: Send) -> bool:
    bannedChannels = database.listBannedChannels()  # type: Iterable[str]
    if bannedChannels:
        send(message.messagesFromItems(bannedChannels, 'Banned Channels: '))
    else:
        send('There are no banned channels')
    return True


def insert_banned_channel(channel: str,
                          reason: str,
                          nick: str,
                          database: DatabaseBase,
                          send: Send) -> bool:
    if channel == bot.config.botnick:
        send('Cannot ban the bot itself')
        return True
    isBannedOrReason = database.isChannelBannedReason(channel)  # type: Optional[str]
    if isBannedOrReason is not None:
        send('{channel} is already banned for: {reason}'.format(
            channel=channel, reason=isBannedOrReason))
        return True
    result = database.addBannedChannel(channel, reason, nick)  # type: bool
    if result:
        database.discardAutoJoin(channel)
        utils.partChannel(channel)

    if result:
        msg = 'Chat {channel} is now banned'
    else:
        msg = 'Chat {channel} could not be banned. Error has occured.'
    send(msg.format(channel=channel))
    return True


def delete_banned_channel(channel: str,
                          reason: str,
                          nick: str,
                          database: DatabaseBase,
                          send: Send) -> bool:
    isBannedOrReason = database.isChannelBannedReason(channel)
    if isBannedOrReason is None:
        send('{channel} is not banned'.format(channel=channel))
        return True
    result = database.removeBannedChannel(channel, reason, nick)

    if result:
        msg = 'Chat {channel} is now unbanned'
    else:
        msg = 'Chat {channel} could not be unbanned. Error has occured.'
    send(msg.format(channel=channel))
    return True
