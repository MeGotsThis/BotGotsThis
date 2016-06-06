from bot import config, utils
from collections import defaultdict
from contextlib import suppress
import datetime


def timeoutUser(db, chat, user, module, baseLevel=0, message=None,
                reason=None):
    properties = ['timeoutLength0', 'timeoutLength1', 'timeoutLength2']
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
    
    timestamp = datetime.datetime.utcnow()
    duration = datetime.timedelta(seconds=config.warningDuration)
    if timestamp - chat.sessionData['timeouts'][module][user][0] >= duration:
        level = baseLevel
    else:
        prevLevel = chat.sessionData['timeouts'][module][user][1]
        level = min(max(baseLevel + 1, prevLevel + 1), 2)
    chat.sessionData['timeouts'][module][user] = (timestamp, level)
    length = timeouts[level]
    if length:
        chat.send(
            '.timeout {user} {length}'.format(user=user, length=length), 0)
    else:
        chat.send('.ban {user}'.format(user=user), 0)
    db.recordTimeout(chat.channel, user, None, module, level, length,
                     message, reason)
    if reason is not None:
        lengthText = '{} seconds'.format(length) if length else 'Banned'
        utils.whisper(
            user,
            '{reason} ({length})'.format(reason=reason, length=lengthText))


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
