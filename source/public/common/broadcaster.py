from bot import config, globals, utils
from ...api import twitch
import time
import json

def botCome(db, channel, send):
    if db.isChannelBannedReason(channel):
        send('Chat ' + channel + ' is banned from joining')
        return True
    priority = db.getAutoJoinsPriority(channel)
    priority = priority if priority is not None else float('inf')
    
    if channel in globals.channels:
        send('I am already in ' + channel)
        return True
    
    response, data = twitch.twitchCall(
        None, 'GET', '/api/channels/' + channel + '/chat_properties')
    chatProperties = json.loads(data.decode('utf-8'))
    
    if chatProperties['eventchat']:
        server = globals.eventChat
    else:
        server = globals.mainChat
    if utils.joinChannel(channel, priority, server):
        send('Joining ' + channel)
    else:
        result = utils.ensureServer(channel, priority, server)
        if result == utils.ENSURE_CORRECT:
            send('Already joined ' + channel)
        elif result == utils.ENSURE_REJOIN_TO_MAIN:
            msg = 'Moved ' + channel + ' to main chat server'
            send(msg)
        elif result == utils.ENSURE_REJOIN_TO_EVENT:
            msg = 'Moved ' + channel + ' to event chat server'
            send(msg)

def botLeave(channel, send):
    if channel == config.botnick:
        return False
    send('Bye ' + channel)
    time.sleep(1)
    utils.partChannel(channel)
    return True

def botEmpty(channel, send):
    if channel in globals.channels:
        globals.messaging.clearQueue(channel)
        send('Cleared all queued messages for ' + channel)

def botAutoJoin(db, channel, send, msgParts):
    if db.isChannelBannedReason(channel):
        send('Chat ' + channel + ' is banned from joining')
        return

    if len(msgParts) >= 2:
        removeMsgs = ['0', 'false', 'no', 'remove', 'rem', 'delete', 'del',
                      'leave', 'part']
        if msgParts[1].lower() in removeMsgs:
            result = db.discardAutoJoin(channel)
            if result:
                send('Auto join for ' + channel + ' is now disabled')
            else:
                send('Auto join for ' + channel + ' was never enabled')
            return True
    
    response, data = twitch.twitchCall(
        None, 'GET', '/api/channels/' + channel + '/chat_properties')
    chatProperties = json.loads(data.decode('utf-8'))
    
    result = db.saveAutoJoin(channel, 0, chatProperties['eventchat'])
    priority = db.getAutoJoinsPriority(channel)
    if result == False:
        db.setAutoJoinServer(channel, chatProperties['eventchat'])
    
    wasInChat = channel in globals.channels
    if chatProperties['eventchat']:
        server = globals.eventChat
    else:
        server = globals.mainChat
    if not wasInChat:
        utils.joinChannel(channel, priority, server)
    else:
        rejoin = utils.ensureServer(channel, priority, server)
    
    if result and not wasInChat:
        send(
            'Auto join for ' + channel + ' is now enabled and joined ' +
            channel + ' chat')
    elif result:
        if rejoin < 0:
            msg = 'Auto join for ' + channel
            msg += ' is now enabled and moved to the correct server'
        else:
            msg = 'Auto join for ' + channel + ' is now enabled'
        send(msg)
    elif not wasInChat:
        send(
            'Auto join for ' + channel + ' is already enabled but now joined ' +
            channel + ' chat')
    else:
        if rejoin < 0:
            msg = 'Auto join for ' + channel
            msg += ' is already enabled and moved to the correct server'
        else:
            msg = 'Auto join for ' + channel
            msg += ' is already enabled and already in chat'
        send(msg)
    return True

def botSetTimeoutLevel(db, channel, send, msgParts):
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
    k = msgParts[0].lower().split('settimeoutlevel-')[1]
    if k not in propertyDict:
        return False
    try:
        value = int(msgParts[1])
    except:
        value = None
    db.setChatProperty(channel, propertyDict[k], value)
    if value is None:
        t = config.moderatorDefaultTimeout[int(k) - 1]
        default = str(t) + ' seconds' if t else 'Banned'
        send('Setting the timeout length for ' + ordinal[k] +
             ' offense to defaulted amount (' + default + ')')
    elif value:
        send('Setting the timeout length for ' + ordinal[k] +
             ' offense to ' + str(value) + ' seconds')
    else:
        send('Setting the timeout length for ' + ordinal[k] +
             ' offense to banning')
    return True
