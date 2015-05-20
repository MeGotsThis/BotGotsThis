from config import config
import database.factory
import ircbot.twitchApi
import ircbot.irc
import email.utils
import datetime
import time
import json

def commandHello(channelData, nick, message, msgParts, permissions):
    channelData.sendMessage('Hello Kappa')
    return True

def commandCome(channelData, nick, message, msgParts, permissions):
    with database.factory.getDatabase() as db:
        if db.isChannelBannedReason(nick):
            channelData.sendMessage('Chat ' + nick + ' is banned from joining')
            return True
        priority = db.getAutoJoinsPriority(nick)
    priority = priority if priority is not None else float('inf')
    
    if ('#' + nick) in ircbot.irc.channels:
        channelData.sendMessage('I am already in ' + nick)
        return True
    
    response, data = ircbot.twitchApi.twitchCall(
        None, 'GET', '/api/channels/' + nick + '/chat_properties')
    chatProperties = json.loads(data.decode('utf-8'))
    
    if ircbot.irc.joinChannel(nick, priority, chatProperties['eventchat']):
        channelData.sendMessage('Joining ' + nick)
    else:
        params = nick, priority, chatProperties['eventchat']
        result = ircbot.irc.ensureServer(*params)
        if result == ircbot.irc.ENSURE_CORRECT:
            channelData.sendMessage('Already joined ' + nick)
        elif result == ircbot.irc.ENSURE_REJOIN_TO_MAIN:
            msg = 'Moved ' + nick + ' to main chat server'
            channelData.sendMessage(msg)
        elif result == ircbot.irc.ENSURE_REJOIN_TO_EVENT:
            msg = 'Moved ' + nick + ' to event chat server'
            channelData.sendMessage(msg)
    return True

def commandLeave(channelData, nick, message, msgParts, permissions):
    if channelData.channel == '#' + config.botnick:
        return False
    channelData.sendMessage('Bye ' + channelData.channel[1:])
    time.sleep(1)
    ircbot.irc.partChannel(channelData.channel)
    return True

def commandEmpty(channelData, nick, message, msgParts, permissions):
    ircbot.irc.messaging.clearQueue(channelData.channel)
    channelData.sendMessage(
        'Cleared all queued messages for ' + channelData.channel[1:])
    return True

def commandAutoJoin(channelData, nick, message, msgParts, permissions):
    with database.factory.getDatabase() as db:
        if db.isChannelBannedReason(nick):
            channelData.sendMessage('Chat ' + nick + ' is banned from joining')
            return True

    if len(msgParts) >= 2:
        removeMsgs = ['0', 'false', 'no', 'remove', 'rem', 'delete', 'del',
                      'leave', 'part']
        if msgParts[1].lower() in removeMsgs:
            with database.factory.getDatabase() as db:
                result = db.discardAutoJoin(nick)
                if result:
                    channelData.sendMessage(
                        'Auto join for ' + nick + ' is now disabled')
                else:
                    channelData.sendMessage(
                        'Auto join for ' + nick + ' was never enabled')
            return True
    
    response, data = ircbot.twitchApi.twitchCall(
        None, 'GET', '/api/channels/' + nick + '/chat_properties')
    chatProperties = json.loads(data.decode('utf-8'))
    
    with database.factory.getDatabase() as db:
        result = db.saveAutoJoin(nick, 0, chatProperties['eventchat'])
        priority = db.getAutoJoinsPriority(nick)
        if result == False:
            db.setAutoJoinServer(nick, chatProperties['eventchat'])
    
    wasInChat = ('#' + nick) in ircbot.irc.channels
    if not wasInChat:
        ircbot.irc.joinChannel(nick, priority, chatProperties['eventchat'])
    else:
        params = nick, priority, chatProperties['eventchat']
        rejoin = ircbot.irc.ensureServer(*params)
    
    if result and not wasInChat:
        channelData.sendMessage(
            'Auto join for ' + nick + ' is now enabled and joined ' +
            nick + ' chat')
    elif result:
        if rejoin < 0:
            msg = 'Auto join for ' + nick
            msg += ' is now enabled and moved to the correct server'
        else:
            msg = 'Auto join for ' + nick + ' is now enabled'
        channelData.sendMessage(msg)
    elif not wasInChat:
        channelData.sendMessage(
            'Auto join for ' + nick + ' is already enabled but now joined ' +
            nick + ' chat')
    else:
        if rejoin < 0:
            msg = 'Auto join for ' + nick
            msg += ' is already enabled and moved to the correct server'
        else:
            msg = 'Auto join for ' + nick
            msg += ' is already enabled and already in chat'
        channelData.sendMessage(msg)
    return True

def commandUptime(channelData, nick, message, msgParts, permissions):
    currentTime = datetime.datetime.utcnow()
    if 'uptime' in channelData.sessionData:
        since = currentTime - channelData.sessionData['uptime']
        if since < datetime.timedelta(seconds=60):
            return False
    channelData.sessionData['uptime'] = currentTime

    chan = channelData.channel[1:]
    response, data = ircbot.twitchApi.twitchCall(
        channelData.channel, 'GET', '/kraken/streams/' + chan,
        headers = {
            'Accept': 'application/vnd.twitchtv.v3+json',
            })
    try:
        if response.status == 200:
            streamData = json.loads(data.decode('utf-8'))
            if streamData['stream']:
                date = response.getheader('Date')
                dateStruct = email.utils.parsedate(date)
                unixTimestamp = time.mktime(dateStruct)
                currentTime = datetime.datetime.fromtimestamp(unixTimestamp)
                params = streamData['stream']['created_at'],
                params += '%Y-%m-%dT%H:%M:%SZ',
                created = datetime.datetime.strptime(*params)
                
                msg = 'Uptime: ' + str(currentTime - created)
                channelData.sendMessage(msg)
                return True
            elif streamData['stream'] is None:
                msg = chan + ' is currently not streaming'                                                                                                                                                                                                                                                                                                                                  
                channelData.sendMessage(msg)
                return True
        raise ValueError()
    except (ValueError, KeyError) as e:
        msg = 'Fail to get stream information from Twitch.tv'
        channelData.sendMessage(msg)
    except Exception as e:
        msg = 'Unknown Error'
        channelData.sendMessage(msg)
    chan = channelData.channel[1:]
