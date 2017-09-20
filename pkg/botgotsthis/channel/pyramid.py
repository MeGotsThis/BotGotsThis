import itertools
import random
from contextlib import suppress
from datetime import timedelta
from typing import Dict, Iterator, List  # noqa: F401

import bot
from source.data import ChatCommandArgs
from source.helper import chat
from source.helper.chat import min_args, permission_feature
from source.helper import timeout


@permission_feature(('broadcaster', None), ('moderator', 'modpyramid'))
@min_args(2)
async def commandPyramid(args: ChatCommandArgs) -> bool:
    count: int = 5 if args.permissions.broadcaster else 3
    # If below generate a ValueError or IndexError,
    # only the above line gets used
    with suppress(ValueError, IndexError):
        count = int(args.message[2])
    return await process_pyramid(args, args.message[1], count)


@permission_feature(('broadcaster', None), ('moderator', 'modpyramid'))
@min_args(2)
async def commandPyramidLong(args: ChatCommandArgs) -> bool:
    count: int = 5 if args.permissions.broadcaster else 3
    with suppress(ValueError, IndexError):
        count = int(args.message.command.split('pyramid-')[1])
    return await process_pyramid(args, args.message.query, count)


async def process_pyramid(args: ChatCommandArgs,
                          repetition: str,
                          count: int) -> bool:
    count = min(count, (bot.config.messageLimit + 1) // (len(repetition) + 1))
    if not args.permissions.broadcaster:
        count = min(count, 5)

        cooldown: timedelta
        cooldown = timedelta(seconds=bot.config.spamModeratorCooldown)
        if chat.inCooldown(args, cooldown, 'modPyramid'):
            return False
    elif not args.permissions.globalModerator:
        count = min(count, 20)
    messages: Iterator[str] = itertools.chain(
        (' '.join((repetition,) * i) for i in range(1, count)),
        (' '.join((repetition,) * i) for i in range(count, 0, -1))
        )
    if args.permissions.chatModerator:
        await timeout.record_timeout(
            args.chat, args.nick, ' '.join((repetition,) * count),
            str(args.message), 'pyramid')
    args.chat.send(messages, -1)
    return True


@permission_feature(('broadcaster', None), ('moderator', 'modpyramid'))
async def commandRandomPyramid(args: ChatCommandArgs) -> bool:
    if not bot.globals.globalEmotes:
        return False
    emotes: Dict[int, str] = bot.globals.globalEmotes.copy()
    count: int = 5 if args.permissions.broadcaster else 3
    # If below generate a ValueError or IndexError,
    # only the above line gets used
    with suppress(ValueError, IndexError):
        count = int(args.message[1])
    rep = []
    if not args.permissions.broadcaster:
        count = min(count, 5)

        cooldown: timedelta
        cooldown = timedelta(seconds=bot.config.spamModeratorCooldown)
        if chat.inCooldown(args, cooldown, 'modPyramid'):
            return False
    elif not args.permissions.globalModerator:
        count = min(count, 20)
    emoteIds: List[int] = list(emotes.keys())
    i: int
    for i in range(count):
        rep.append(emotes[random.choice(emoteIds)])
        if len(' '.join(rep)) > bot.config.messageLimit:
            del rep[-1]
            count = len(rep)
            break
    messages: Iterator[str] = itertools.chain(
        (' '.join(rep[0:i]) for i in range(1, count)),
        (' '.join(rep[0:i]) for i in range(count, 0, -1)))
    args.chat.send(messages, -1)
    return True
