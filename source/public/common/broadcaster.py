from bot import config, globals, utils
from ...api import twitch
from ...database.factory import getDatabase
import time
import json

def botCome(channel, sendMessage):
    with getDatabase() as db:
        if db.isChannelBannedReason(channel):
            sendMessage('Chat ' + channel + ' is banned from joining')
            return True
        priority = db.getAutoJoinsPriority(channel)
    priority = priority if priority is not None else float('inf')
    
    if channel in globals.channels:
        sendMessage('I am already in ' + channel)
        return True
    
    response, data = twitch.twitchCall(
        None, 'GET', '/api/channels/' + channel + '/chat_properties')
    chatProperties = json.loads(data.decode('utf-8'))
    
    if chatProperties['eventchat']:
        server = globals.eventChat
    else:
        server = globals.mainChat
    if globals.joinChannel(channel, priority, server):
        sendMessage('Joining ' + channel)
    else:
        result = globals.ensureServer(channel, priority, server)
        if result == globals.ENSURE_CORRECT:
            sendMessage('Already joined ' + channel)
        elif result == globals.ENSURE_REJOIN_TO_MAIN:
            msg = 'Moved ' + channel + ' to main chat server'
            sendMessage(msg)
        elif result == globals.ENSURE_REJOIN_TO_EVENT:
            msg = 'Moved ' + channel + ' to event chat server'
            sendMessage(msg)

def botLeave(channel, sendMessage):
    if channel == config.botnick:
        return False
    sendMessage('Bye ' + channel)
    time.sleep(1)
    utils.partChannel(channel)
    return True

def botEmpty(channel, sendMessage):
    if channel in globals.channels:
        globals.messaging.clearQueue(channel)
        sendMessage('Cleared all queued messages for ' + channel)

def botAutoJoin(channel, sendMessage, msgParts):
    with getDatabase() as db:
        if db.isChannelBannedReason(channel):
            sendMessage('Chat ' + channel + ' is banned from joining')
            return

    if len(msgParts) >= 2:
        removeMsgs = ['0', 'false', 'no', 'remove', 'rem', 'delete', 'del',
                      'leave', 'part']
        if msgParts[1].lower() in removeMsgs:
            with getDatabase() as db:
                result = db.discardAutoJoin(channel)
                if result:
                    sendMessage(
                        'Auto join for ' + channel + ' is now disabled')
                else:
                    sendMessage(
                        'Auto join for ' + channel + ' was never enabled')
            return True
    
    response, data = twitch.twitchCall(
        None, 'GET', '/api/channels/' + channel + '/chat_properties')
    chatProperties = json.loads(data.decode('utf-8'))
    
    with getDatabase() as db:
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
        sendMessage(
            'Auto join for ' + channel + ' is now enabled and joined ' +
            channel + ' chat')
    elif result:
        if rejoin < 0:
            msg = 'Auto join for ' + channel
            msg += ' is now enabled and moved to the correct server'
        else:
            msg = 'Auto join for ' + channel + ' is now enabled'
        sendMessage(msg)
    elif not wasInChat:
        sendMessage(
            'Auto join for ' + channel + ' is already enabled but now joined ' +
            channel + ' chat')
    else:
        if rejoin < 0:
            msg = 'Auto join for ' + channel
            msg += ' is already enabled and moved to the correct server'
        else:
            msg = 'Auto join for ' + channel
            msg += ' is already enabled and already in chat'
        sendMessage(msg)
    return True
