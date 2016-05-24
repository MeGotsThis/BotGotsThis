from bot import config, globals
from collections import defaultdict
from contextlib import suppress
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
        chat.sessionData['timeouts'] = defaultdict(
            lambda: defaultdict(
                lambda: (datetime.datetime.min, 0)))
    
    utcnow = datetime.datetime.utcnow()
    duration = datetime.timedelta(seconds=config.warningDuration)
    if utcnow - chat.sessionData['timeouts'][module][user][0] >= duration:
        level = baseLevel
    else:
        prevLevel = chat.sessionData['timeouts'][module][user][1]
        level = min(max(baseLevel + 1, prevLevel + 1), 2)
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

def recordTimeoutFromCommand(db, chat, user, messages, sourceMessage,
                             module='custom'):
    if not isinstance(messages, (list, tuple)):
        messages = [messages]
    for message in messages:
        length = None
        who = None
        if message.startswith(('.ban', '/ban')):
            with suppress(ValueError, IndexError):
                who = message.split()[1]
                length = 0
        if message.startswith(('.timeout', '/timeout')):
            with suppress(ValueError, IndexError):
                parts = message.split()
                length = int(parts[2])
                who = parts[1]
        if length is not None:
            db.recordTimeout(chat.channel, who, user, module, None, length,
                             sourceMessage, None)
