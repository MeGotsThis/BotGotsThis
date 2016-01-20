from bot import config, globals
import datetime

def timeoutUser(db, chat, user, module, baseLevel=0, message=None,
                reason=None):
    properties = ['timeoutLength0', 'timeoutLength1', 'timeoutLength2',]
    defaults = {'timeoutLength0': config.moderatorDefaultTimeout[0],
                'timeoutLength1': config.moderatorDefaultTimeout[1],
                'timeoutLength2': config.moderatorDefaultTimeout[2],
                }
    chatProp = db.getChatProperties(chat.channel, properties, defaults, int)
    timeouts = chatProp['timeoutLength0'], chatProp['timeoutLength1'],
    timeouts += chatProp['timeoutLength2'],
    
    if 'timeouts' not in chat.sessionData:
        chat.sessionData['timeouts'] = {}
    if module not in chat.sessionData['timeouts']:
        chat.sessionData['timeouts'][module] = {}
    
    utcnow = datetime.datetime.utcnow()
    duration = datetime.timedelta(seconds=config.warningDuration)
    if (user not in chat.sessionData['timeouts'][module] or
        utcnow - chat.sessionData['timeouts'][module][user][0] >= duration):
        level = baseLevel
    else:
        prevLevel = chat.sessionData['timeouts'][module][user][1]
        level = min(max(baseLevel + 1, prevLevel + 1), 3)
    chat.sessionData['timeouts'][module][user] = (utcnow, level)
    length = timeouts[level]
    if length:
        chat.sendMessage('.timeout ' + user + ' ' + str(length), 0)
    else:
        chat.sendMessage('.ban ' + user, 0)
    db.recordTimeout(chat.channel, user, None, module, level, length,
                     message, reason)
    if reason is not None:
        l = str(length) + ' seconds' if length else 'Banned'
        globals.messaging.queueWhisper(user, reason + ' (' + l + ')')

def recordTimeoutFromCommand(db, chat, user, message, sourceMessage,
                             module='custom'):
    length = None
    who = None
    if message.startswith(('.ban', '/ban')):
        try:
            who = message.split()[1]
            length = 0
        except:
            pass
    if message.startswith(('.timeout', '/timeout')):
        try:
            parts = message.split()
            length = int(parts[2])
            who = parts[0]
        except:
            pass
    if length is not None:
        db.recordTimeout(chat.channel, who, user, module, None, length,
                         sourceMessage, reason)
