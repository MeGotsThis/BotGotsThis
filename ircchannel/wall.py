from config import config
import database.factory
import ircbot.irc
import datetime

def commandWall(channelData, nick, message, msgParts, permissions):
    with database.factory.getDatabase() as db:
        if (not db.hasFeature(channelData.channel[1:], 'modwall') and
            not permissions['broadcaster']):
            return False
    if len(msgParts) < 2:
        return False
    rep = msgParts[1] + ' '
    if permissions['broadcaster']:
        length = 5
        rows = 20
    else:
        length = 3
        rows = 5
    try:
        if len(msgParts) == 3:
            rows = int(msgParts[2])
        else:
            length = int(msgParts[2])
            rows = int(msgParts[3])
    except:
        pass
    length = min(length, (2048 - 11 - len(channelData.channel)) // len(rep))
    if not permissions['broadcaster']:
        length = min(length, 5)
        rows = min(rows, 10)
        
        currentTime = datetime.datetime.utcnow()
        cooldown = datetime.timedelta(seconds=config.spamModeratorCooldown)
        if 'modWall' in channelData.sessionData:
            since = currentTime - channelData.sessionData['modWall']
            if since < cooldown:
                return False
        channelData.sessionData['modWall'] = currentTime
    elif not permissions['globalMod']:
        length = min(length, 20)
        rows = min(rows, 500)
    messages = [rep * length + ('' if i % 2 == 0 else ' \ufeff')
                for i in range(rows)]
    channelData.sendMulipleMessages(messages, 2)
    return True

def commandWallLong(channelData, nick, message, msgParts, permissions):
    with database.factory.getDatabase() as db:
        if (not db.hasFeature(channelData.channel[1:], 'modwall') and
            not permissions['broadcaster']):
            return False
    msgParts = message.split(None, 1)
    if len(msgParts) < 2:
        return False
    try:
        rows = int(msgParts[0].split('-')[1])
    except:
        if permissions['broadcaster']:
            rows = 20
        else:
            rows = 5
    if not permissions['broadcaster']:
        rows = min(rows, 10)
        
        currentTime = datetime.datetime.utcnow()
        cooldown = datetime.timedelta(seconds=config.spamModeratorCooldown)
        if 'modWall' in channelData.sessionData:
            since = currentTime - channelData.sessionData['modWall']
            if since < cooldown:
                return False
        channelData.sessionData['modWall'] = currentTime
    elif not permissions['globalMod']:
        rows = min(rows, 500)
    messages = [msgParts[1] + ('' if i % 2 == 0 else ' \ufeff')
                for i in range(rows)]
    channelData.sendMulipleMessages(messages, 2)
    return True
