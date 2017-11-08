from lib.data import ChatCommandArgs
from lib.database import DatabaseTimeout
from lib.helper.chat import min_args, permission


@permission('moderator')
@permission('chatModerator')
@min_args(2)
async def commandPurge(args: ChatCommandArgs) -> bool:
    user: str = args.message[1]
    reason: str = args.message[2:]
    args.chat.send(f'.timeout {user} 1 {reason}')
    db: DatabaseTimeout
    async with DatabaseTimeout.acquire() as db:
        await db.recordTimeout(
            args.chat.channel, args.message.lower[1], args.nick, 'purge', None,
            1, str(args.message), reason if reason else None)
    return True
