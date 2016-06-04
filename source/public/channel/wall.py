from ..library import timeout
from ..library.chat import inCooldown, min_args, permission_feature
from bot import config
from contextlib import suppress
from datetime import timedelta

@permission_feature(('broadcaster', None), ('moderator', 'modwall'))
@min_args(2)
def commandWall(args):
    rep = args.message[1] + ' '
    length, rows = (5, 20) if args.permissions.broadcaster else (3, 5)
    # If below generate a ValueError, only the above line gets used
    with suppress(ValueError, IndexError):
        length, rows = length, int(args.message[2])
        # If this line generate an IndexError it does not get evaluated
        length, rows = rows, int(args.message[3])
    length = min(length, config.messageLimit // len(rep))
    if not args.permissions.broadcaster:
        length, rows = min(length, 5), min(rows, 10)
        
        cooldown = timedelta(seconds=config.spamModeratorCooldown)
        if inCooldown(args, cooldown, 'modWall'):
            return False
    elif not args.permissions.globalModerator:
        length, rows = min(length, 20), min(rows, 500)
    spacer = '' if args.permissions.chatModerator else ' \ufeff'
    messages = (rep * length + ('' if i % 2 == 0 else spacer)
                for i in range(rows))
    args.chat.send(messages, -1)
    return True

@permission_feature(('broadcaster', None), ('moderator', 'modwall'))
@min_args(2)
def commandWallLong(args):
    rows = 20 if args.permissions.broadcaster else 5
    # If below generate a ValueError or IndexError,
    # only the above line gets used
    with suppress(ValueError, IndexError):
        rows = int(args.message.command.split('wall-')[1])
    if not args.permissions.broadcaster:
        rows = min(rows, 10)
        
        cooldown = timedelta(seconds=config.spamModeratorCooldown)
        if inCooldown(args, cooldown, 'modWall'):
            return False
    elif not args.permissions.globalModerator:
        rows = min(rows, 500)
    spacer = '' if args.permissions.chatModerator else ' \ufeff'
    messages = (args.message.query + ('' if i % 2 == 0 else spacer)
                for i in range(rows))
    args.chat.send(messages, -1)
    if args.permissions.chatModerator:
        timeout.recordTimeoutFromCommand(
            args.database, args.chat, args.nick, args.message.query,
            args.message, 'wall')
    return True
