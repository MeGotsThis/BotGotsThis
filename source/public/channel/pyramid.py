from ..common import timeout
from bot import config, globals
import datetime
import random

def commandPyramid(db, chat, tags, nick, message, msgParts, permissions, now):
    if (not db.hasFeature(chat.channel, 'modpyramid') and
        not permissions['broadcaster']):
        return False
    
    if len(msgParts) < 2:
        return False
    rep = msgParts[1] + ' '
    try:
        count = int(msgParts[2])
    except:
        if permissions['broadcaster']:
            count = 5
        else:
            count = 3
    count = min(count, config.messageLimit // len(rep))
    if not permissions['broadcaster']:
        count = min(count, 5)
        
        currentTime = datetime.datetime.utcnow()
        cooldown = datetime.timedelta(seconds=config.spamModeratorCooldown)
        if 'modPyramid' in chat.sessionData:
            since = currentTime - chat.sessionData['modPyramid']
            if since < cooldown:
                return False
        chat.sessionData['modPyramid'] = currentTime
    elif not permissions['globalMod']:
        count = min(count, 20)
    messages = [rep * i for i in range(1, count)]
    messages += [rep * i for i in range(count, 0, -1)]
    chat.sendMulipleMessages(messages, 2)
    return True

def commandRPyramid(db, chat, tags, nick, message, msgParts, permissions, now):
    if (not db.hasFeature(chat.channel, 'modpyramid') and
        not permissions['broadcaster']):
        return False
    
    emotes = globals.globalEmotes
    
    try:
        count = int(msgParts[1])
    except:
        if permissions['broadcaster']:
            count = 5
        else:
            count = 3
    rep = []
    if not permissions['broadcaster']:
        count = min(count, 5)
        
        currentTime = datetime.datetime.utcnow()
        cooldown = datetime.timedelta(seconds=config.spamModeratorCooldown)
        if 'modPyramid' in chat.sessionData:
            since = currentTime - chat.sessionData['modPyramid']
            if since < cooldown:
                return False
        chat.sessionData['modPyramid'] = currentTime
    elif not permissions['globalMod']:
        count = min(count, 20)
    emoteIds = list(emotes.keys())
    for i in range(count):
        rep.append(emotes[random.choice(emoteIds)])
        if len(' '.join(rep)) > config.messageLimit:
            del rep[-1]
            break
    messages = [' '.join(rep[0:i]) for i in range(1, count)]
    messages += [' '.join(rep[0:i]) for i in range(count, 0, -1)]
    chat.sendMulipleMessages(messages, 2)
    return True

def commandPyramidLong(db, chat, tags, nick, message, msgParts, permissions,
                       now):
    if (not db.hasFeature(chat.channel, 'modpyramid') and
        not permissions['broadcaster']):
        return False
    
    msgParts = message.split(None, 1)
    if len(msgParts) < 2:
        return False
    rep = msgParts[1] + ' '
    try:
        count = int(msgParts[0].lower().split('pyramid-')[1])
    except:
        if permissions['broadcaster']:
            count = 5
        else:
            count = 3
    count = min(count, config.messageLimit // len(rep))
    if not permissions['broadcaster']:
        count = min(count, 5)
        
        currentTime = datetime.datetime.utcnow()
        cooldown = datetime.timedelta(seconds=config.spamModeratorCooldown)
        if 'modPyramid' in chat.sessionData:
            since = currentTime - chat.sessionData['modPyramid']
            if since < cooldown:
                return False
        chat.sessionData['modPyramid'] = currentTime
    elif not permissions['globalMod']:
        count = min(count, 20)
    messages = [rep * i for i in range(1, count)]
    messages += [rep * i for i in range(count, 0, -1)]
    chat.sendMulipleMessages(messages, 2)
    if permissions['channelModerator']:
        timeout.recordTimeoutFromCommand(db, chat, nick,
                                         messages[len(messages)//2], message,
                                         'pyramid')
    return True
