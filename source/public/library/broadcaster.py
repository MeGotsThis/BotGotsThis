from ...api import twitch
from bot import config, globals, utils
import json
import time

def botCome(db, channel, send):
    if db.isChannelBannedReason(channel):
        send('Chat {channel} is banned from joining'.format(channel=channel))
        return True
    priority = db.getAutoJoinsPriority(channel)
    priority = priority if priority is not None else float('inf')
    
    if channel in globals.channels:
        send('I am already in {channel}'.format(channel=channel))
        return True
    
    cluster = twitch.twitchChatServer(channel)
    if utils.joinChannel(channel, priority, cluster):
        send('Joining {channel}'.format(channel=channel))
    else:
        result = utils.ensureServer(channel, priority, server)
        if result == utils.ENSURE_CORRECT:
            send('Already joined {channel}'.format(channel=channel))
        elif result == utils.ENSURE_REJOIN:
            send('Moved {channel} to correct chat '
                 'server'.format(channel=channel))

def botLeave(channel, send):
    if channel == config.botnick:
        return False
    send('Bye {channel}'.format(channel=channel))
    time.sleep(1)
    utils.partChannel(channel)
    return True

def botEmpty(channel, send):
    if channel in globals.channels:
        globals.channels[channel].socket.messaging.clearChat(channel)
        send('Cleared all queued messages '
             'for {channel}'.format(channel=channel))

def botAutoJoin(db, channel, send, message):
    if db.isChannelBannedReason(channel):
        send('Chat {channel} is banned from '
             'joining'.format(channel=channel))
        return

    if len(message) >= 2:
        removeMsgs = ['0', 'false', 'no', 'remove', 'rem', 'delete', 'del',
                      'leave', 'part']
        if message.lower[1] in removeMsgs:
            result = db.discardAutoJoin(channel)
            if result:
                send('Auto join for {channel} is now '
                     'disabled'.format(channel=channel))
            else:
                send('Auto join for {channel} was never '
                     'enabled'.format(channel=channel))
            return True
    
    cluster = twitch.twitchChatServer(channel)
    result = db.saveAutoJoin(channel, 0, cluster)
    priority = db.getAutoJoinsPriority(channel)
    if result is False:
        db.setAutoJoinServer(channel, cluster)
    
    wasInChat = channel in globals.channels
    if not wasInChat:
        utils.joinChannel(channel, priority, cluster)
    else:
        rejoin = utils.ensureServer(channel, priority, cluster)
    
    if result and not wasInChat:
        msg = ('Auto join for {channel} is now enabled and joined {channel} '
               'chat')
    elif result:
        if rejoin < 0:
            msg = ('Auto join for {channel} is now enabled and moved to the '
                   'correct server')
        else:
            msg = 'Auto join for {channel} is now enabled'
    elif not wasInChat:
        msg = ('Auto join for {channel} is already enabled but now joined '
               '{channel} chat')
    else:
        if rejoin < 0:
            msg = ('Auto join for {channel} is already enabled and moved to '
                   'the correct server')
        else:
            msg = ('Auto join for {channel} is already enabled and already '
                   'in chat')
    send(msg.format(channel=channel))
    return True

def botSetTimeoutLevel(db, channel, send, message):
    propertyDict = {
        '1': 'timeoutLength0',
        '2': 'timeoutLength1',
        '3': 'timeoutLength2',
        }
    ordinal = {
        '1': '1st',
        '2': '2nd',
        '3': '3rd',
        }
    k = message.command.split('settimeoutlevel-')[1]
    if k not in propertyDict:
        return False
    try:
        value = int(message[1])
    except (ValueError, IndexError):
        value = None
    timeout = config.moderatorDefaultTimeout[int(k) - 1]
    default = '{} seconds'.format(timeout) if timeout else 'Banned'
    db.setChatProperty(channel, propertyDict[k], value)
    if value is None:
        msg = ('Setting the timeout length for {ordinal} offense to defaulted '
               'amount ({default})')
    elif value:
        msg = ('Setting the timeout length for {ordinal} offense to {value} '
               'seconds')
    else:
        msg = 'Setting the timeout length for {ordinal} offense to banning'
    send(msg.format(ordinal=ordinal[k], default=default, value=value))
    return True
