from bot import utils
from typing import Iterable, List, Optional
from ..library.message import messagesFromItems
from ...data import ManageBotArgs

needReason = ['add', 'insert', 'del', 'delete', 'rem', 'remove', 'remove']  # type: List[str]


def manageBanned(args: ManageBotArgs) -> bool:
    if len(args.message) < 3:
        return False
    if args.message.lower[2] in ['list']:
        bannedChannels = args.database.listBannedChannels()  # type: Iterable[str]
        if bannedChannels:
            args.send(messagesFromItems(bannedChannels, 'Banned Channels: '))
        else:
            args.send('There are no banned channels')
        return True
    
    if len(args.message) < 5:
        if args.message.lower[2] in needReason:
            args.send(args.nick + ' -> Reason needs to be specified')
        return False
    channel = args.message.lower[3]  # type: str
    if args.message.lower[2] in ['add', 'insert']:
        isBannedOrReason = args.database.isChannelBannedReason(channel)  # type: Optional[str]
        if isBannedOrReason:
            args.send('{channel} is already banned for: {reason}'.format(
                channel=channel, reason=isBannedOrReason))
            return True
        result = args.database.addBannedChannel(channel, args.message[4:],
                                                args.nick)  # type: bool
        if result:
            args.database.discardAutoJoin(channel)
            utils.partChannel(channel)
            
        if result:
            msg = 'Chat {channel} is now banned'
        else:
            msg = 'Chat {channel} could not be banned. Error has occured.'
        args.send(msg.format(channel=channel))
        return True
    if args.message.lower[2] in ['del', 'delete', 'rem', 'remove', 'remove']:
        isBannedOrReason = args.database.isChannelBannedReason(channel)
        if not isBannedOrReason:
            args.send('{channel} is not banned'.format(channel=channel))
            return False
        params = channel, args.message[4:], args.nick
        result = args.database.removeBannedChannel(*params)
            
        if result:
            msg = 'Chat {channel} is now unbanned'
        else:
            msg = 'Chat {channel} could not be unbanned. Error has occured.'
        args.send(msg.format(channel=channel))
        return True
    return False
