from config import config
import database.factory
import ircbot.irc
import datetime
import random

def commandPyramid(channelData, nick, message, msgParts, permissions):
    with database.factory.getDatabase() as db:
        if (not db.hasFeature(channelData.channel[1:], 'modpyramid') and
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
    count = min(count, 1000 // len(rep))
    if not permissions['broadcaster']:
        count = min(count, 5)
        
        currentTime = datetime.datetime.utcnow()
        cooldown = datetime.timedelta(seconds=config.spamModeratorCooldown)
        if 'modPyramid' in channelData.sessionData:
            since = currentTime - channelData.sessionData['modPyramid']
            if since < cooldown:
                return False
        channelData.sessionData['modPyramid'] = currentTime
    elif not permissions['globalMod']:
        count = min(count, 20)
    messages = [rep * i for i in range(1, count)]
    messages += [rep * i for i in range(count, 0, -1)]
    channelData.sendMulipleMessages(messages, 2)
    return True

def commandRPyramid(channelData, nick, message, msgParts, permissions):
    with database.factory.getDatabase() as db:
        if (not db.hasFeature(channelData.channel[1:], 'modpyramid') and
            not permissions['broadcaster']):
            return False
    
    emotes = ircbot.irc.globalEmotes
    
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
        if 'modPyramid' in channelData.sessionData:
            since = currentTime - channelData.sessionData['modPyramid']
            if since < cooldown:
                return False
        channelData.sessionData['modPyramid'] = currentTime
    elif not permissions['globalMod']:
        count = min(count, 20)
    emoteIds = list(emotes.keys())
    for i in range(count):
        rep.append(emotes[random.choice(emoteIds)])
        if len(' '.join(rep)) > 1000:
            del rep[-1]
            break
    messages = [' '.join(rep[0:i]) for i in range(1, count)]
    messages += [' '.join(rep[0:i]) for i in range(count, 0, -1)]
    channelData.sendMulipleMessages(messages, 2)
    return True

def commandPyramidLong(channelData, nick, message, msgParts, permissions):
    with database.factory.getDatabase() as db:
        if (not db.hasFeature(channelData.channel[1:], 'modpyramid') and
            not permissions['broadcaster']):
            return False
    msgParts = message.split(None, 1)
    if len(msgParts) < 2:
        return False
    rep = msgParts[1] + ' '
    try:
        count = int(msgParts[0].split('-')[1])
    except:
        if permissions['broadcaster']:
            count = 5
        else:
            count = 3
    count = min(count, 1000 // len(rep))
    if not permissions['broadcaster']:
        count = min(count, 5)
        
        currentTime = datetime.datetime.utcnow()
        cooldown = datetime.timedelta(seconds=config.spamModeratorCooldown)
        if 'modPyramid' in channelData.sessionData:
            since = currentTime - channelData.sessionData['modPyramid']
            if since < cooldown:
                return False
        channelData.sessionData['modPyramid'] = currentTime
    elif not permissions['globalMod']:
        count = min(count, 20)
    messages = [rep * i for i in range(1, count)]
    messages += [rep * i for i in range(count, 0, -1)]
    channelData.sendMulipleMessages(messages, 2)
    return True
