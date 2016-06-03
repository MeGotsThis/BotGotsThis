from ..library import timeout
from ..library.chat import inCooldown, min_args, permission
from bot import config
from contextlib import suppress
import datetime

@min_args(2)
@permission('moderator')
def commandWall(args):
    if (not args.database.hasFeature(args.chat.channel, 'modwall') and
        not args.permissions.broadcaster):
        return False
    
    rep = args.message[1] + ' '
    if args.permissions.broadcaster:
        length = 5
        rows = 20
    else:
        length = 3
        rows = 5
    with suppress(ValueError):
        if len(args.message) == 3:
            rows = int(args.message[2])
        else:
            length = int(args.message[2])
            rows = int(args.message[3])
    length = min(length, config.messageLimit // len(rep))
    if not args.permissions.broadcaster:
        length = min(length, 5)
        rows = min(rows, 10)
        
        cooldown = datetime.timedelta(seconds=config.spamModeratorCooldown)
        if 'modWall' in args.chat.sessionData:
            since = args.timestamp - args.chat.sessionData['modWall']
            if since < cooldown:
                return False
        args.chat.sessionData['modWall'] = args.timestamp
    elif not args.permissions.globalModerator:
        length = min(length, 20)
        rows = min(rows, 500)
    spacer = '' if args.permissions.chatModerator else ' \ufeff'
    messages = [rep * length + ('' if i % 2 == 0 else spacer)
                for i in range(rows)]
    args.chat.send(messages, -1)
    return True

@min_args(2)
@permission('moderator')
def commandWallLong(args):
    if (not args.database.hasFeature(args.chat.channel, 'modwall') and
        not args.permissions.broadcaster):
        return False
    
    try:
        rows = int(args.message.command.split('wall-')[1])
    except:
        if args.permissions.broadcaster:
            rows = 20
        else:
            rows = 5
    if not args.permissions.broadcaster:
        rows = min(rows, 10)
        
        cooldown = datetime.timedelta(seconds=config.spamModeratorCooldown)
        if 'modWall' in args.chat.sessionData:
            since = args.timestamp - args.chat.sessionData['modWall']
            if since < cooldown:
                return False
        args.chat.sessionData['modWall'] = args.timestamp
    elif not args.permissions.globalModerator:
        rows = min(rows, 500)
    spacer = '' if args.permissions.chatModerator else ' \ufeff'
    messages = [args.message.query + ('' if i % 2 == 0 else spacer)
                for i in range(rows)]
    args.chat.send(messages, -1)
    if args.permissions.chatModerator:
        timeout.recordTimeoutFromCommand(args.database, args.chat, args.nick,
                                         messages[0], args.message, 'wall')
    return True
