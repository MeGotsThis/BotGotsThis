import bot.config
from ..library import chat, timeout
from ..library.chat import min_args, permission_feature
from ...data import ChatCommandArgs
from contextlib import suppress
from datetime import timedelta
from typing import Iterator


@permission_feature(('broadcaster', None), ('moderator', 'modwall'))
@min_args(2)
async def commandWall(args: ChatCommandArgs) -> bool:
    length, rows = (5, 20) if args.permissions.broadcaster else (3, 5)
    # If below generate a ValueError, only the above line gets used
    with suppress(ValueError, IndexError):
        length, rows = length, int(args.message[2])
        # If this line generate an IndexError it does not get evaluated
        length, rows = rows, int(args.message[3])
    limit = (bot.config.messageLimit + 1) // (len(args.message[1]) + 1)
    length = min(length, limit)
    message: str = ' '.join((args.message[1],) * length)
    return await process_wall(args, message, rows)


@permission_feature(('broadcaster', None), ('moderator', 'modwall'))
@min_args(2)
async def commandWallLong(args: ChatCommandArgs) -> bool:
    rows = 20 if args.permissions.broadcaster else 5
    # If below generate a ValueError or IndexError,
    # only the above line gets used
    with suppress(ValueError, IndexError):
        rows = int(args.message.command.split('wall-')[1])
    return await process_wall(args, args.message.query, rows)


async def process_wall(args: ChatCommandArgs,
                       repetition: str,
                       rows: int) -> bool:
    if not args.permissions.broadcaster:
        rows = min(rows, 10)

        cooldown: timedelta
        cooldown = timedelta(seconds=bot.config.spamModeratorCooldown)
        if chat.inCooldown(args, cooldown, 'modWall'):
            return False
    elif not args.permissions.globalModerator:
        rows = min(rows, 500)
    spacer: str = '' if args.permissions.chatModerator else ' \ufeff'
    messages: Iterator[str] = (repetition + ('' if i % 2 == 0 else spacer)
                               for i in range(rows))
    args.chat.send(messages, -1)
    if args.permissions.chatModerator:
        await timeout.record_timeout(args.chat, args.nick, repetition,
                                     str(args.message), 'wall')
    return True
