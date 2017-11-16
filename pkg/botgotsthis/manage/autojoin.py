from contextlib import suppress
from typing import Optional  # noqa: F401
from lib.data import ManageBotArgs, Send
from lib.database import DatabaseMain
from pkg.channel import library as autojoin


async def manageAutoJoin(args: ManageBotArgs) -> bool:
    db: DatabaseMain
    if len(args.message) < 3:
        return False

    if len(args.message) < 4:
        return False

    bannedWithReason: Optional[str]
    async with DatabaseMain.acquire() as db:
        bannedWithReason = await db.isChannelBannedReason(
            args.message.lower[3])
    if bannedWithReason is not None:
        channel: str = args.message.lower[3]
        args.send(f'Chat {channel} is banned from joining')
        return True

    if args.message.lower[2] in ['add', 'insert', 'join']:
        async with DatabaseMain.acquire() as db:
            return await autojoin.auto_join_add(
                db, args.message.lower[3], args.send)
    if args.message.lower[2] in ['del', 'delete', 'rem', 'remove', 'part']:
        async with DatabaseMain.acquire() as db:
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
    db: DatabaseMain
    async with DatabaseMain.acquire() as db:
        result = await db.setAutoJoinPriority(channel, priority)
    if result:
        send(f'Auto join for {channel} is set to priority {priority}')
    else:
        send(f'Auto join for {channel} was never enabled')
    return True
