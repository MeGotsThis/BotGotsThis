from typing import cast

from lib import database
from lib.data import ChatCommandArgs
from lib.helper.chat import min_args, permission


@permission('moderator')
@permission('chatModerator')
@min_args(2)
async def commandPurge(args: ChatCommandArgs) -> bool:
    user: str = args.message[1]
    reason: str = args.message[2:]
    args.chat.send(f'.timeout {user} 1 {reason}')
    db_: database.Database
    async with database.get_database(database.Schema.Timeout) as db_:
        db: database.DatabaseTimeout = cast(database.DatabaseTimeout, db_)
        await db.recordTimeout(
            args.chat.channel, args.message.lower[1], args.nick, 'purge', None,
            1, str(args.message), reason if reason else None)
    return True
