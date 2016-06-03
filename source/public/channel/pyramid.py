from ..library import timeout
from ..library.chat import inCooldown, permission
from bot import config, globals
from datetime import timedelta
import random

@permission('moderator')
def commandPyramid(args):
    if (not args.database.hasFeature(args.chat.channel, 'modpyramid') and
        not args.permissions.broadcaster):
        return False
    
    if len(args.message) < 2:
        return False
    rep = args.message[1] + ' '
    try:
        count = int(args.message[2])
    except:
        if args.permissions.broadcaster:
            count = 5
        else:
            count = 3
    count = min(count, config.messageLimit // len(rep))
    if not args.permissions.broadcaster:
        count = min(count, 5)
        
        cooldown = timedelta(seconds=config.spamModeratorCooldown)
        if inCooldown(args, cooldown, 'modPyramid'):
            return False
    elif not args.permissions.globalModerator:
        count = min(count, 20)
    messages = [rep * i for i in range(1, count)]
    messages += [rep * i for i in range(count, 0, -1)]
    args.chat.sendMulipleMessages(messages, 2)
    return True

@permission('moderator')
def commandRPyramid(args):
    if (not args.database.hasFeature(args.chat.channel, 'modpyramid') and
        not args.permissions.broadcaster):
        return False
    
    emotes = globals.globalEmotes
    
    try:
        count = int(args.message[1])
    except:
        if args.permissions.broadcaster:
            count = 5
        else:
            count = 3
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
    messages = [' '.join(rep[0:i]) for i in range(1, count)]
    messages += [' '.join(rep[0:i]) for i in range(count, 0, -1)]
    args.chat.sendMulipleMessages(messages, 2)
    return True

@permission('moderator')
def commandPyramidLong(args):
    if (not args.database.hasFeature(chat.channel, 'modpyramid') and
        not args.permissions.broadcaster):
        return False
    
    if len(args.message) < 2:
        return False
    rep = args.message.query + ' '
    try:
        count = int(args.message.command.split('pyramid-')[1])
    except:
        if args.permissions.broadcaster:
            count = 5
        else:
            count = 3
    count = min(count, config.messageLimit // len(rep))
    if not args.permissions.broadcaster:
        count = min(count, 5)
        
        cooldown = timedelta(seconds=config.spamModeratorCooldown)
        if inCooldown(args, cooldown, 'modPyramid'):
            return False
    elif not args.permissions.globalModerator:
        count = min(count, 20)
    messages = [rep * i for i in range(1, count)]
    messages += [rep * i for i in range(count, 0, -1)]
    args.chat.sendMulipleMessages(messages, 2)
    if args.permissions.chatModerator:
        timeout.recordTimeoutFromCommand(args.database, args.chat, args.nick,
                                         messages[len(messages)//2], 
                                         str(args.message), 'pyramid')
    return True
