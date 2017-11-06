from bot import utils
from contextlib import suppress
from typing import Optional  # noqa: F401
from lib import database
from lib.api import twitch
from lib.data import AutoJoinChannel, ManageBotArgs, Send  # noqa: F401
from pkg.channel import library as autojoin


async def manageAutoJoin(args: ManageBotArgs) -> bool:
    db: database.DatabaseMain
    if len(args.message) < 3:
        return False
    if args.message.lower[2] in ['reloadserver']:
        return await reload_server(args.send)

    if len(args.message) < 4:
        return False

    bannedWithReason: Optional[str]
    async with database.get_main_database() as db:
        bannedWithReason = await db.isChannelBannedReason(
            args.message.lower[3])
    if bannedWithReason is not None:
        channel: str = args.message.lower[3]
        args.send(f'Chat {channel} is banned from joining')
        return True

    if args.message.lower[2] in ['add', 'insert', 'join']:
        async with database.get_main_database() as db:
            return await autojoin.auto_join_add(
                db, args.message.lower[3], args.send)
    if args.message.lower[2] in ['del', 'delete', 'rem', 'remove', 'part']:
        async with database.get_main_database() as db:
            return await autojoin.auto_join_delete(
                db, args.message.lower[3], args.send)
    if args.message.lower[2] in ['pri', 'priority']:
        priority: int = 0
        with suppress(ValueError, IndexError):
            priority = int(args.message[4])
        return await auto_join_priority(
            args.message.lower[3], priority, args.send)
    return False


async def auto_join_priority(channel: str,
                             priority: int,
                             send: Send) -> bool:
    result: bool
    async with database.get_main_database() as db:
        result = await db.setAutoJoinPriority(channel, priority)
    if result:
        send(f'Auto join for {channel} is set to priority {priority}')
    else:
        send(f'Auto join for {channel} was never enabled')
    return True


async def reload_server(send: Send) -> bool:
    db: database.DatabaseMain
    async with database.get_main_database() as db:
        autojoin: AutoJoinChannel
        async for autojoin in db.getAutoJoinsChats():
            cluster: Optional[str]
            cluster = await twitch.chat_server(autojoin.broadcaster)
            if cluster is not None and autojoin.cluster != cluster:
                await db.setAutoJoinServer(autojoin.broadcaster, cluster)
                utils.ensureServer(autojoin.broadcaster, autojoin.priority,
                                   cluster)
                print(f'{utils.now()} Set Server for {autojoin.broadcaster}')
    send('Auto Join reload server complete')
    return True
