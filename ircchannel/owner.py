from config import config
import privatechannel.manageBot
import database.factory
import ircbot.irc
import threading
import datetime
import time
import json
import sys

def commandExit(channelData, nick, message, msgParts, permissions):
    channelData.sendMessage('Goodbye Keepo', 0)
    time.sleep(0.5)
    for channel in set(ircbot.irc.channels.keys()):
        ircbot.irc.partChannel(channel)
    ircbot.irc.messaging.running = False
    return True

def commandSay(channelData, nick, message, msgParts, permissions):
    if (permissions['owner'] and permissions['ownerChan']):
        msgParts = message.split(None, 2)
        if msgParts[1][0] != '#':
            msgParts[1] = '#' + msgParts[1]
        if msgParts[1] in ircbot.irc.channels:
            ircbot.irc.channels[msgParts[1]].sendMessage(msgParts[2])
        return True
    return False

def commandJoin(channelData, nick, message, msgParts, permissions):
    if len(msgParts) < 2:
        return False
    params = channelData, msgParts
    threading.Thread(target=threadJoin, args=params).start()
    return True

def threadJoin(channelData, msgParts):
    chan = msgParts[1].lower()
    
    with database.factory.getDatabase() as db:
        priority = db.getAutoJoinsPriority(chan)
    priority = priority if priority is not None else float('inf')
    
    response, data = ircbot.twitchApi.twitchCall(
        None, 'GET', '/api/channels/' + chan + '/chat_properties')
    chatProperties = json.loads(data.decode('utf-8'))
    
    if chan[0] != '#':
        chan = '#' + chan
    if ircbot.irc.joinChannel(chan, priority, chatProperties['eventchat']):
        channelData.sendMessage('Joining ' + chan[1:])
    else:
        params = chan, priority, chatProperties['eventchat']
        result = ircbot.irc.ensureServer(*params)
        if result == ircbot.irc.ENSURE_CORRECT:
            channelData.sendMessage('Already joined ' + chan[1:])
        elif result == ircbot.irc.ENSURE_REJOIN_TO_MAIN:
            msg = 'Moved ' + chan[1:] + ' to main chat server'
            channelData.sendMessage(msg)
        elif result == ircbot.irc.ENSURE_REJOIN_TO_EVENT:
            msg = 'Moved ' + chan[1:] + ' to event chat server'
            channelData.sendMessage(msg)

def commandPart(channelData, nick, message, msgParts, permissions):
    if len(msgParts) < 2:
        return False
    chan = msgParts[1].lower()
    if chan[0] != '#':
        chan = '#' + chan
    ircbot.irc.partChannel(chan)
    channelData.sendMessage('Leaving ' + chan[1:])
    return True

def commandEmptyAll(channelData, nick, message, msgParts, permissions):
    ircbot.irc.messaging.clearAllQueue()
    channelData.sendMessage('Cleared all queued msgs')
    return True

def commandEmpty(channelData, nick, message, msgParts, permissions):
    if msgParts[1][0] != '#':
        msgParts[1] = '#' + msgParts[1].lower()
    ircbot.irc.messaging.clearQueue(msgParts[1])
    channelData.sendMessage(
        'Cleared all queued messages for ' + msgParts[1][1:])
    return True

def commandManageBot(channelData, nick, message, msgParts, permissions):
    if len(msgParts) < 2:
        return False
    
    methods = {
        'listchats': manageListChats,
        }
    threadMethods = {
        'autojoin': threadManageAutoJoin,
        }

    methods = dict(
        list(methods.items()) + 
        list(privatechannel.manageBot.methods.items()))
    threadMethods = dict(
        list(threadMethods.items()) +
        list(privatechannel.manageBot.threadMethods.items()))

    params = channelData, message, msgParts
    
    if msgParts[1].lower() in methods:
        methods[msgParts[1].lower()](*params)
    elif msgParts[1].lower() in threadMethods:
        threading.Thread(
            target=threadMethods[msgParts[1].lower()], args=params).start()
    
    return True

def manageListChats(channelData, message, msgParts):
    channels = [c[1:] for c in ircbot.irc.channels.keys()]
    channelData.sendMessage('Twitch Chats: ' + ', '.join(channels))

def threadManageAutoJoin(channelData, message, msgParts):
    if len(msgParts) < 3:
        return
    if msgParts[2] in ['reloadserver']:
        with database.factory.getDatabase() as db:
            for channelRow in db.getAutoJoinsChats():
                uri = '/api/channels/' + channelRow['broadcaster']
                uri += '/chat_properties'
                r = ircbot.twitchApi.twitchCall(None, 'GET', uri)
                response, data = r
                chatProperties = json.loads(data.decode('utf-8'))
                
                if channelRow['eventServer'] != chatProperties['eventchat']:
                    params = channelRow['broadcaster'],
                    params += chatProperties['eventchat'],
                    db.setAutoJoinServer(*params)
                    
                    params = channelRow['broadcaster'],
                    params += channelRow['priority'],
                    params += chatProperties['eventchat'],
                    rejoin = ircbot.irc.ensureServer(*params)
                    
                    print('Set Server for ' + channelRow['broadcaster'])
        channelData.sendMessage('Auto Join reload server complete')
    
    if len(msgParts) < 4:
        return
    msgParts[3] = msgParts[3].lower()
    if msgParts[2] in ['add', 'insert', 'join']:
        response, data = ircbot.twitchApi.twitchCall(
            None, 'GET', '/api/channels/' + msgParts[3] + '/chat_properties')
        chatProperties = json.loads(data.decode('utf-8'))
        
        with database.factory.getDatabase() as db:
            params = msgParts[3], 0, chatProperties['eventchat']
            result = db.saveAutoJoin(*params)
            priority = db.getAutoJoinsPriority(msgParts[3])
            if result == False:
                db.setAutoJoinServer(msgParts[3], chatProperties['eventchat'])
            
        wasInChat = ('#' + msgParts[3]) in ircbot.irc.channels
        if not wasInChat:
            params = msgParts[3], priority, chatProperties['eventchat']
            ircbot.irc.joinChannel(*params)
        else:
            params = msgParts[3], priority, chatProperties['eventchat']
            rejoin = ircbot.irc.ensureServer(*params)
        
        if result and not wasInChat:
            channelData.sendMessage(
                'Auto join for ' + msgParts[3] + ' is now enabled and '
                'joined ' + msgParts[3] + ' chat')
        elif result:
            if rejoin < 0:
                msg = 'Auto join for ' + msgParts[3]
                msg += ' is now enabled and moved to the correct server'
            else:
                msg = 'Auto join for ' + msgParts[3] + ' is now enabled'
            channelData.sendMessage(msg)
        elif not wasInChat:
            channelData.sendMessage(
                'Auto join for ' + msgParts[3] + ' is already enabled but '
                'now joined ' + msgParts[3] + ' chat')
        else:
            if rejoin < 0:
                msg = 'Auto join for ' + msgParts[3]
                msg += ' is already enabled and moved to the correct server'
            else:
                msg = 'Auto join for ' + msgParts[3]
                msg += ' is already enabled and already in chat'
            channelData.sendMessage(msg)
    if msgParts[2] in ['del', 'delete', 'rem', 'remove', 'remove']:
        with database.factory.getDatabase() as db:
            result = db.discardAutoJoin(msgParts[3])
            if result:
                channelData.sendMessage(
                    'Auto join for ' + msgParts[3] + ' is now disabled')
            else:
                channelData.sendMessage(
                    'Auto join for ' + msgParts[3] + ' was never enabled')
    if msgParts[2] in ['pri', 'priority']:
        try:
            priority = int(msgParts[4])
        except Exception:
            priority = 0
        with database.factory.getDatabase() as db:
            result = db.setAutoJoinPriority(msgParts[3], priority)
            if result:
                channelData.sendMessage(
                    'Auto join for ' + msgParts[3] + ' is set to '
                    'priority ' + str(priority))
            else:
                channelData.sendMessage(
                    'Auto join for ' + msgParts[3] + ' was never enabled')
