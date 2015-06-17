from config import config
import database.factory
import ircbot.twitchApi
import ircbot.irc
import time
import json

def botCome(channel, sendMessage):
    with database.factory.getDatabase() as db:
        if db.isChannelBannedReason(channel):
            sendMessage('Chat ' + channel + ' is banned from joining')
            return True
        priority = db.getAutoJoinsPriority(channel)
    priority = priority if priority is not None else float('inf')
    
    if ('#' + channel) in ircbot.irc.channels:
        sendMessage('I am already in ' + channel)
        return True
    
    response, data = ircbot.twitchApi.twitchCall(
        None, 'GET', '/api/channels/' + channel + '/chat_properties')
    chatProperties = json.loads(data.decode('utf-8'))
    
    if chatProperties['eventchat']:
        server = ircbot.irc.eventChat
    else:
        server = ircbot.irc.mainChat
    if ircbot.irc.joinChannel(channel, priority, server):
        channelData.sendMessage('Joining ' + channel)
    else:
        result = ircbot.irc.ensureServer(channel, priority, server)
        if result == ircbot.irc.ENSURE_CORRECT:
            sendMessage('Already joined ' + channel)
        elif result == ircbot.irc.ENSURE_REJOIN_TO_MAIN:
            msg = 'Moved ' + channel + ' to main chat server'
            sendMessage(msg)
        elif result == ircbot.irc.ENSURE_REJOIN_TO_EVENT:
            msg = 'Moved ' + channel + ' to event chat server'
            sendMessage(msg)

def botLeave(channel, sendMessage):
    if channel == '#' + config.botnick:
        return False
    sendMessage('Bye ' + channel[1:])
    time.sleep(1)
    ircbot.irc.partChannel(channel)
    return True

def botEmpty(channel, sendMessage):
    if channel in ircbot.irc.channels:
        ircbot.irc.messaging.clearQueue(channel)
        sendMessage('Cleared all queued messages for ' + channel[1:])

def botAutoJoin(channel, sendMessage, msgParts):
    with database.factory.getDatabase() as db:
        if db.isChannelBannedReason(channel):
            sendMessage('Chat ' + channel + ' is banned from joining')
            return

    if len(msgParts) >= 2:
        removeMsgs = ['0', 'false', 'no', 'remove', 'rem', 'delete', 'del',
                      'leave', 'part']
        if msgParts[1].lower() in removeMsgs:
            with database.factory.getDatabase() as db:
                result = db.discardAutoJoin(channel)
                if result:
                    sendMessage(
                        'Auto join for ' + channel + ' is now disabled')
                else:
                    sendMessage(
                        'Auto join for ' + channel + ' was never enabled')
            return True
    
    response, data = ircbot.twitchApi.twitchCall(
        None, 'GET', '/api/channels/' + channel + '/chat_properties')
    chatProperties = json.loads(data.decode('utf-8'))
    
    with database.factory.getDatabase() as db:
        result = db.saveAutoJoin(channel, 0, chatProperties['eventchat'])
        priority = db.getAutoJoinsPriority(channel)
        if result == False:
            db.setAutoJoinServer(channel, chatProperties['eventchat'])
    
    wasInChat = ('#' + channel) in ircbot.irc.channels
    if chatProperties['eventchat']:
        server = ircbot.irc.eventChat
    else:
        server = ircbot.irc.mainChat
    if not wasInChat:
        ircbot.irc.joinChannel(channel, priority, server)
    else:
        rejoin = ircbot.irc.ensureServer(channel, priority, server)
    
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
