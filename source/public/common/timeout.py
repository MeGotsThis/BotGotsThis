from bot import config, globals
import datetime

def timeoutUser(db, channel, user, module, baseLevel=0, message=None,
                reason=None):
    timeouts = db.getTimeoutLengths(channel.channel)
    
    if 'timeouts' not in channel.sessionData:
        channel.sessionData['timeouts'] = {}
    
    utcnow = datetime.datetime.utcnow()
    duration = datetime.timedelta(seconds=config.warningDuration)
    if (user not in channel.sessionData['timeouts'] or
        utcnow - channel.sessionData['timeouts'][user][0] >= duration):
        level = baseLevel
    else:
        prevLevel = channel.sessionData['timeouts'][user][1]
        level = min(max(baseLevel + 1, prevLevel + 1), 3)
    channel.sessionData['timeouts'][user] = (utcnow, level)
    length = timeouts[level]
    if length:
        channel.sendMessage('.timeout ' + user + ' ' + str(length), 0)
    else:
        channel.sendMessage('.ban ' + user, 0)
    db.recordTimeout(channel.channel, user, None, module, level, length,
                     message, reason)
    if reason is not None:
        l = str(length) + ' seconds' if length else 'Banned'
        globals.messaging.queueWhisper(user, reason + ' (' + l + ')')

def recordTimeoutFromCommand(db, channel, user, message, sourceMessage,
                             module='custom'):
    length = None
    who = None
    if message.startswith('.ban'):
        try:
            who = message.split()[1]
            length = 0
        except:
            pass
    if message.startswith('.timeout'):
        try:
            parts = message.split()
            length = int(parts[2])
            who = parts[0]
        except:
            pass
    if length is not None:
        db.recordTimeout(channel.channel, who, user, module, None, length,
                         sourceMessage, reason)
