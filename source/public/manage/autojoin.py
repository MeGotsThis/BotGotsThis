from bot import utils
from contextlib import suppress
from typing import Optional
from ..library import broadcaster
from ...api import twitch
from ...database import AutoJoinChannel, DatabaseMain
from ...data import ManageBotArgs, Send


async def manageAutoJoin(args: ManageBotArgs) -> bool:
    if len(args.message) < 3:
        return False
    if args.message.lower[2] in ['reloadserver']:
        return await reload_server(args.database, args.send)
    
    if len(args.message) < 4:
        return False

    if args.database.isChannelBannedReason(args.message.lower[3]) is not None:
        args.send('Chat {channel} is banned from joining'.format(
            channel=args.message.lower[3]))
        return True

    if args.message.lower[2] in ['add', 'insert', 'join']:
        return await broadcaster.auto_join_add(
            args.database, args.message.lower[3], args.send)
    if args.message.lower[2] in ['del', 'delete', 'rem', 'remove' ,'part']:
        return broadcaster.auto_join_delete(
            args.database, args.message.lower[3], args.send)
    if args.message.lower[2] in ['pri', 'priority']:
        priority: int = 0
        with suppress(ValueError, IndexError):
            priority = int(args.message[4])
        return auto_join_priority(
            args.database, args.message.lower[3], priority, args.send)
    return False


def auto_join_priority(database: DatabaseMain,
                       channel: str,
                       priority: int,
                       send: Send) -> bool:
        result: bool = database.setAutoJoinPriority(channel, priority)
        if result:
            send('Auto join for {channel} is set to priority '
                 '{priority}'.format(channel=channel, priority=priority))
        else:
            send('Auto join for {channel} was never '
                 'enabled'.format(channel=channel))
        return True


async def reload_server(database: DatabaseMain,
                  send: Send) -> bool:
    autojoin: AutoJoinChannel
    async for autojoin in database.getAutoJoinsChats():
        cluster: Optional[str] = await twitch.chat_server(autojoin.broadcaster)
        if cluster is not None and autojoin.cluster != cluster:
            database.setAutoJoinServer(autojoin.broadcaster, cluster)
            utils.ensureServer(autojoin.broadcaster, autojoin.priority,
                               cluster)
            print('{time} Set Server for {channel}'.format(
                time=utils.now(), channel=autojoin.broadcaster))
    send('Auto Join reload server complete')
    return True
