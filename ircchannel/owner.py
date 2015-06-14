from config import config
import botcommands.channel
import botcommands.exit
import database.factory
import ircbot.twitchApi
import ircbot.irc
import datetime
import time
import json
import sys
try:
    import privatechannel.manageBot as manageBot
except:
    import privatechannel.default.manageBot as manageBot

def commandExit(channelData, nick, message, msgParts, permissions):
    botcommands.exit.botExit(channelData.sendMessage)
    return True

def commandSay(channelData, nick, message, msgParts, permissions):
    msgParts = message.split(None, 2)
    if msgParts[1][0] != '#':
        msgParts[1] = '#' + msgParts[1]
    if msgParts[1] in ircbot.irc.channels:
        botcommands.channel.botSay(msgParts[1], msgParts[2])
    return True

def commandJoin(channelData, nick, message, msgParts, permissions):
    if len(msgParts) < 2:
        return False

    chan = msgParts[1].lower()
    if chan[0] != '#':
        chan = '#' + chan
    
    botcommands.channel.botJoin(chan, channelData.sendMessage)
    return True

def commandPart(channelData, nick, message, msgParts, permissions):
    if len(msgParts) < 2:
        return False
    chan = msgParts[1].lower()
    if chan[0] != '#':
        chan = '#' + chan
    botcommands.channel.botPart(chan, channelData.sendMessage)
    return True

def commandEmptyAll(channelData, nick, message, msgParts, permissions):
    botcommands.channel.botEmptyAll(channelData.sendMessage)
    return True

def commandEmpty(channelData, nick, message, msgParts, permissions):
    if len(msgParts) < 2:
        return False
    if msgParts[1][0] != '#':
        msgParts[1] = '#' + msgParts[1].lower()
    botcommands.channel.botEmpty(msgParts[1], channelData.sendMessage)
    return True

def commandManageBot(channelData, nick, message, msgParts, permissions):
    if len(msgParts) < 2:
        return False
    
    methods = {
        'listchats': manageListChats,
        'autojoin': manageAutoJoin,
        'banned': manageBanned,
        }

    methods = dict(list(methods.items()) + list(manageBot.methods.items()))

    params = channelData, nick, message, msgParts
    
    if msgParts[1].lower() in methods:
        return methods[msgParts[1].lower()](*params)
    return False

def manageListChats(channelData, nick, message, msgParts):
    channels = [c[1:] for c in ircbot.irc.channels.keys()]
    channelData.sendMessage('Twitch Chats: ' + ', '.join(channels))
    return True

def manageAutoJoin(channelData, nick, message, msgParts):
    if len(msgParts) < 3:
        return False
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
                    
                    if chatProperties['eventServer']:
                        server = ircbot.irc.eventChat
                    else:
                        server = ircbot.irc.mainChat
                    params = channelRow['broadcaster'], channelRow['priority'],
                    params += server,
                    rejoin = ircbot.irc.ensureServer(*params)
                    
                    print(str(datetime.datetime.utcnow()) + ' Set Server ' +
                          'for ' + channelRow['broadcaster'])
        channelData.sendMessage('Auto Join reload server complete')
        return True
    
    if len(msgParts) < 4:
        return False
    msgParts[3] = msgParts[3].lower()
    if msgParts[2] in ['add', 'insert', 'join']:
        response, data = ircbot.twitchApi.twitchCall(
            None, 'GET', '/api/channels/' + msgParts[3] + '/chat_properties')
        chatProperties = json.loads(data.decode('utf-8'))
        
        with database.factory.getDatabase() as db:
            if db.isChannelBannedReason(msgParts[3]):
                channelData.sendMessage('Chat ' + msgParts[3] +
                                        ' is banned from joining')
                return True
            if chatProperties['eventServer']:
                server = ircbot.irc.eventChat
            else:
                server = ircbot.irc.mainChat
            result = db.saveAutoJoin(msgParts[3], 0, server)
            priority = db.getAutoJoinsPriority(msgParts[3])
            if result == False:
                db.setAutoJoinServer(msgParts[3], chatProperties['eventchat'])
            
        wasInChat = ('#' + msgParts[3]) in ircbot.irc.channels
        if chatProperties['eventServer']:
            server = ircbot.irc.eventChat
        else:
            server = ircbot.irc.mainChat
        if not wasInChat:
            ircbot.irc.joinChannel(msgParts[3], priority, server)
        else:
            rejoin = ircbot.irc.ensureServer(msgParts[3], priority, server)
        
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
        return True
    if msgParts[2] in ['del', 'delete', 'rem', 'remove', 'remove']:
        with database.factory.getDatabase() as db:
            result = db.discardAutoJoin(msgParts[3])
            if result:
                channelData.sendMessage(
                    'Auto join for ' + msgParts[3] + ' is now disabled')
            else:
                channelData.sendMessage(
                    'Auto join for ' + msgParts[3] + ' was never enabled')
        return True
    if msgParts[2] in ['pri', 'priority']:
        try:
            priority = int(msgParts[4])
        except:
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
        return True
    return False

def manageBanned(channelData, nick, message, msgParts):
    if len(msgParts) < 3:
        return False
    if msgParts[2] in ['list']:
        with database.factory.getDatabase() as db:
            bannedChannels = db.listBannedChannels()
            if bannedChannels:
                msg = 'Banned Channels: ' + ', '.join(bannedChannels)
                channelData.sendMessage(msg)
            else:
                channelData.sendMessage('There are no banned channels')
        return True
    
    if len(msgParts) < 5:
        if msgParts[2] in ['add', 'insert', 'del', 'delete',
                           'rem', 'remove', 'remove']:
            channelData.sendMessage(nick + ' -> Reason needs to be specified')
        return False
    msgParts = message.split(None, 4)
    channel = msgParts[3].lower()
    if msgParts[2] in ['add', 'insert']:
        with database.factory.getDatabase() as db:
            isBannedOrReason = db.isChannelBannedReason(channel)
            if isBannedOrReason:
                channelData.sendMessage(
                    channel + ' is already banned for: ' + isBannedOrReason)
                return False
            params = channel, msgParts[4], nick
            result = db.addBannedChannel(*params)
            if result:
                db.discardAutoJoin(channel)
                ircbot.irc.partChannel(channel)
            
        if result:
            channelData.sendMessage('Chat ' + channel + ' is now banned')
        else:
            channelData.sendMessage('Chat ' + channel + ' could not be '
                                    'banned. Error has occured.')
        return True
    if msgParts[2] in ['del', 'delete', 'rem', 'remove', 'remove']:
        with database.factory.getDatabase() as db:
            isBannedOrReason = db.isChannelBannedReason(channel)
            if not isBannedOrReason:
                channelData.sendMessage(
                    channel + ' is not banned')
                return False
            params = channel, msgParts[4], nick
            result = db.removeBannedChannel(*params)
            
        if result:
            channelData.sendMessage(channel + ' is now unbanned')
        else:
            channelData.sendMessage(channel + ' could not be unbanned. '
                                    'Error has occured.')
        return True
    return False
