from ...database.factory import getDatabase
from bot import globals, utils
from lists.manage import methods
import json

def botManageBot(sendMessage, nick, message, msgParts):
    params = sendMessage, nick, message, msgParts
    
    if msgParts[1].lower() in methods:
        return methods[msgParts[1].lower()](*params)
    return False

def manageListChats(sendMessage, nick, message, msgParts):
    channels = [c[1:] for c in globals.channels.keys()]
    sendMessage('Twitch Chats: ' + ', '.join(channels))
    return True

def manageAutoJoin(sendMessage, nick, message, msgParts):
    if len(msgParts) < 3:
        return False
    if msgParts[2] in ['reloadserver']:
        with getDatabase() as db:
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
                    
                    if chatProperties['eventchat']:
                        server = globals.eventChat
                    else:
                        server = globals.mainChat
                    params = channelRow['broadcaster'], channelRow['priority'],
                    params += server,
                    rejoin = utils.ensureServer(*params)
                    
                    print(str(datetime.datetime.utcnow()) + ' Set Server ' +
                          'for ' + channelRow['broadcaster'])
        sendMessage('Auto Join reload server complete')
        return True
    
    if len(msgParts) < 4:
        return False
    msgParts[3] = msgParts[3].lower()
    if msgParts[2] in ['add', 'insert', 'join']:
        response, data = ircbot.twitchApi.twitchCall(
            None, 'GET', '/api/channels/' + msgParts[3] + '/chat_properties')
        chatProperties = json.loads(data.decode('utf-8'))
        
        with getDatabase() as db:
            if db.isChannelBannedReason(msgParts[3]):
                sendMessage('Chat ' + msgParts[3] + ' is banned from joining')
                return True
            if chatProperties['eventchat']:
                server = globals.eventChat
            else:
                server = globals.mainChat
            params = msgParts[3], 0, chatProperties['eventchat']
            result = db.saveAutoJoin(*params)
            priority = db.getAutoJoinsPriority(msgParts[3])
            if result == False:
                db.setAutoJoinServer(msgParts[3], chatProperties['eventchat'])
            
        wasInChat = msgParts[3] in globals.channels
        if chatProperties['eventchat']:
            server = globals.eventChat
        else:
            server = globals.mainChat
        if not wasInChat:
            utils.joinChannel(msgParts[3], priority, server)
        else:
            rejoin = utils.ensureServer(msgParts[3], priority, server)
        
        if result and not wasInChat:
            sendMessage('Auto join for ' + msgParts[3] + ' is now enabled and '
                        'joined ' + msgParts[3] + ' chat')
        elif result:
            if rejoin < 0:
                msg = 'Auto join for ' + msgParts[3]
                msg += ' is now enabled and moved to the correct server'
            else:
                msg = 'Auto join for ' + msgParts[3] + ' is now enabled'
            sendMessage(msg)
        elif not wasInChat:
            sendMessage('Auto join for ' + msgParts[3] + ' is already enabled '
                        'but now joined ' + msgParts[3] + ' chat')
        else:
            if rejoin < 0:
                msg = 'Auto join for ' + msgParts[3]
                msg += ' is already enabled and moved to the correct server'
            else:
                msg = 'Auto join for ' + msgParts[3]
                msg += ' is already enabled and already in chat'
            sendMessage(msg)
        return True
    if msgParts[2] in ['del', 'delete', 'rem', 'remove', 'remove']:
        with getDatabase() as db:
            result = db.discardAutoJoin(msgParts[3])
            if result:
                sendMessage('Auto join for ' + msgParts[3] + ' is now '
                            'disabled')
            else:
                sendMessage('Auto join for ' + msgParts[3] + ' was never '
                            'enabled')
        return True
    if msgParts[2] in ['pri', 'priority']:
        try:
            priority = int(msgParts[4])
        except:
            priority = 0
        with getDatabase() as db:
            result = db.setAutoJoinPriority(msgParts[3], priority)
            if result:
                sendMessage('Auto join for ' + msgParts[3] + ' is set to '
                            'priority ' + str(priority))
            else:
                sendMessage('Auto join for ' + msgParts[3] + ' was never '
                            'enabled')
        return True
    return False

def manageBanned(sendMessage, nick, message, msgParts):
    if len(msgParts) < 3:
        return False
    if msgParts[2] in ['list']:
        with getDatabase() as db:
            bannedChannels = db.listBannedChannels()
            if bannedChannels:
                msg = 'Banned Channels: ' + ', '.join(bannedChannels)
                sendMessage(msg)
            else:
                sendMessage('There are no banned channels')
        return True
    
    if len(msgParts) < 5:
        if msgParts[2] in ['add', 'insert', 'del', 'delete',
                           'rem', 'remove', 'remove']:
            sendMessage(nick + ' -> Reason needs to be specified')
        return False
    msgParts = message.split(None, 4)
    channel = msgParts[3].lower()
    if msgParts[2] in ['add', 'insert']:
        with getDatabase() as db:
            isBannedOrReason = db.isChannelBannedReason(channel)
            if isBannedOrReason:
                sendMessage(channel + ' is already banned for: ' +
                            isBannedOrReason)
                return False
            params = channel, msgParts[4], nick
            result = db.addBannedChannel(*params)
            if result:
                db.discardAutoJoin(channel)
                utils.partChannel(channel)
            
        if result:
            sendMessage('Chat ' + channel + ' is now banned')
        else:
            sendMessage('Chat ' + channel + ' could not be banned. '
                        'Error has occured.')
        return True
    if msgParts[2] in ['del', 'delete', 'rem', 'remove', 'remove']:
        with getDatabase() as db:
            isBannedOrReason = db.isChannelBannedReason(channel)
            if not isBannedOrReason:
                sendMessage(channel + ' is not banned')
                return False
            params = channel, msgParts[4], nick
            result = db.removeBannedChannel(*params)
            
        if result:
            sendMessage(channel + ' is now unbanned')
        else:
            sendMessage(channel + ' could not be unbanned. Error has occured.')
        return True
    return False
