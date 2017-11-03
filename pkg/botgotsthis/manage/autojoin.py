from bot import utils
from contextlib import suppress
from typing import Optional  # noqa: F401
from lib.api import twitch
from lib.database import DatabaseMain  # noqa: F401
from lib.data import AutoJoinChannel, ManageBotArgs, Send
from pkg.channel import library as autojoin


async def manageAutoJoin(args: ManageBotArgs) -> bool:
    if len(args.message) < 3:
        return False
    if args.message.lower[2] in ['reloadserver']:
        return await reload_server(args.database, args.send)

    if len(args.message) < 4:
        return False

    bannedWithReason: Optional[str]
    bannedWithReason = await args.database.isChannelBannedReason(
        args.message.lower[3])
    if bannedWithReason is not None:
        channel: str = args.message.lower[3]
        args.send(f'Chat {channel} is banned from joining')
        return True

    if args.message.lower[2] in ['add', 'insert', 'join']:
        return await autojoin.auto_join_add(
            args.database, args.message.lower[3], args.send)
    if args.message.lower[2] in ['del', 'delete', 'rem', 'remove', 'part']:
        return await autojoin.auto_join_delete(
            args.database, args.message.lower[3], args.send)
    if args.message.lower[2] in ['pri', 'priority']:
        priority: int = 0
        with suppress(ValueError, IndexError):
            priority = int(args.message[4])
        return await auto_join_priority(
            args.database, args.message.lower[3], priority, args.send)
    return False


async def auto_join_priority(database: DatabaseMain,
                             channel: str,
                             priority: int,
                             send: Send) -> bool:
    result: bool = await database.setAutoJoinPriority(channel, priority)
    if result:
        send(f'Auto join for {channel} is set to priority {priority}')
    else:
        send(f'Auto join for {channel} was never enabled')
    return True


async def reload_server(database: DatabaseMain,
                        send: Send) -> bool:
    autojoin: AutoJoinChannel
    async for autojoin in database.getAutoJoinsChats():
        cluster: Optional[str] = await twitch.chat_server(autojoin.broadcaster)
        if cluster is not None and autojoin.cluster != cluster:
            await database.setAutoJoinServer(autojoin.broadcaster, cluster)
            utils.ensureServer(autojoin.broadcaster, autojoin.priority,
                               cluster)
            print(f'{utils.now()} Set Server for {autojoin.broadcaster}')
    send('Auto Join reload server complete')
    return True
