from ..common import timeout
from bot import config
import datetime

def commandWall(db, chat, tags, nick, message, permissions, now):
    if (not db.hasFeature(chat.channel, 'modwall') and
        not permissions.broadcaster):
        return False
    
    if len(message) < 2:
        return False
    rep = message[1] + ' '
    if permissions.broadcaster:
        length = 5
        rows = 20
    else:
        length = 3
        rows = 5
    try:
        if len(message) == 3:
            rows = int(message[2])
        else:
            length = int(message[2])
            rows = int(message[3])
    except:
        pass
    length = min(length, config.messageLimit // len(rep))
    if not permissions.broadcaster:
        length = min(length, 5)
        rows = min(rows, 10)
        
        currentTime = datetime.datetime.utcnow()
        cooldown = datetime.timedelta(seconds=config.spamModeratorCooldown)
        if 'modWall' in chat.sessionData:
            since = currentTime - chat.sessionData['modWall']
            if since < cooldown:
                return False
        chat.sessionData['modWall'] = currentTime
    elif not permissions.globalModerator:
        length = min(length, 20)
        rows = min(rows, 500)
    spacer = '' if permissions.chatModerator else ' \ufeff'
    messages = [rep * length + ('' if i % 2 == 0 else spacer)
                for i in range(rows)]
    chat.sendMulipleMessages(messages, 2)
    return True

def commandWallLong(db, chat, tags, nick, message, permissions, now):
    if (not db.hasFeature(chat.channel, 'modwall') and
        not permissions.broadcaster):
        return False
    
    if len(message) < 2:
        return False
    try:
        rows = int(message.command.split('wall-')[1])
    except:
        if permissions.broadcaster:
            rows = 20
        else:
            rows = 5
    if not permissions.broadcaster:
        rows = min(rows, 10)
        
        currentTime = datetime.datetime.utcnow()
        cooldown = datetime.timedelta(seconds=config.spamModeratorCooldown)
        if 'modWall' in chat.sessionData:
            since = currentTime - chat.sessionData['modWall']
            if since < cooldown:
                return False
        chat.sessionData['modWall'] = currentTime
    elif not permissions.globalModerator:
        rows = min(rows, 500)
    spacer = '' if permissions.chatModerator else ' \ufeff'
    messages = [message.query + ('' if i % 2 == 0 else spacer)
                for i in range(rows)]
    chat.sendMulipleMessages(messages, 2)
    if permissions.chatModerator:
        timeout.recordTimeoutFromCommand(db, chat, nick, messages[0],
                                         message, 'wall')
    return True
