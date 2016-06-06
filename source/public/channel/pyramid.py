import itertools
import random
from contextlib import suppress
from datetime import timedelta
from bot import config, globals
from ..library import timeout
from ..library.chat import inCooldown, min_args, permission_feature


@permission_feature(('broadcaster', None), ('moderator', 'modpyramid'))
@min_args(2)
def commandPyramid(args):
    count = 5 if args.permissions.broadcaster else 3
    # If below generate a ValueError or IndexError,
    # only the above line gets used
    with suppress(ValueError, IndexError):
        count = int(args.message[2])
    return processPyramid(args, args.message[1] + ' ', count)

@permission_feature(('broadcaster', None), ('moderator', 'modpyramid'))
@min_args(2)
def commandPyramidLong(args):
    count = 5 if args.permissions.broadcaster else 3
    with suppress(ValueError, IndexError):
        count = int(args.message.command.split('pyramid-')[1])
    return processPyramid(args, args.message.query + ' ', count)

def processPyramid(args, repetition, count):
    count = min(count, config.messageLimit // len(repetition))
    if not args.permissions.broadcaster:
        count = min(count, 5)
        
        cooldown = timedelta(seconds=config.spamModeratorCooldown)
        if inCooldown(args, cooldown, 'modPyramid'):
            return False
    elif not args.permissions.globalModerator:
        count = min(count, 20)
    messages = itertools.chain((repetition * i for i in range(1, count)),
                               (repetition * i for i in range(count, 0, -1)))
    if args.permissions.chatModerator:
        timeout.recordTimeoutFromCommand(
            args.database, args.chat, args.nick, repetition * count,
            str(args.message), 'pyramid')
    args.chat.send(messages, -1)
    return True

@permission_feature(('broadcaster', None), ('moderator', 'modpyramid'))
def commandRPyramid(args):
    emotes = globals.globalEmotes
    count = 5 if args.permissions.broadcaster else 3
    # If below generate a ValueError or IndexError,
    # only the above line gets used
    with suppress(ValueError, IndexError):
        count = int(args.message[1])
    rep = []
    if not args.permissions.broadcaster:
        count = min(count, 5)
        
        cooldown = timedelta(seconds=config.spamModeratorCooldown)
        if inCooldown(args, cooldown, 'modPyramid'):
            return False
    elif not args.permissions.globalModerator:
        count = min(count, 20)
    emoteIds = list(emotes.keys())
    for i in range(count):
        rep.append(emotes[random.choice(emoteIds)])
        if len(' '.join(rep)) > config.messageLimit:
            del rep[-1]
            break
    messages = itertools.chain(
        (' '.join(rep[0:i]) for i in range(1, count)),
        (' '.join(rep[0:i]) for i in range(count, 0, -1)))
    args.chat.send(messages, -1)
    return True
