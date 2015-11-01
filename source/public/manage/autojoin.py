from ...api import twitch
from bot import globals, utils
import json

def manageAutoJoin(db, send, nick, message, msgParts):
    if len(msgParts) < 3:
        return False
    if msgParts[2] in ['reloadserver']:
        for channelRow in db.getAutoJoinsChats():
            uri = '/api/channels/' + channelRow['broadcaster']
            uri += '/chat_properties'
            r = twitch.twitchCall(None, 'GET', uri)
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
                    
                print(str(datetime.datetime.utcnow()) + ' Set Server for ' +
                      channelRow['broadcaster'])
        send('Auto Join reload server complete')
        return True
    
    if len(msgParts) < 4:
        return False
    msgParts[3] = msgParts[3].lower()
    if msgParts[2] in ['add', 'insert', 'join']:
        response, data = twitch.twitchCall(
            None, 'GET', '/api/channels/' + msgParts[3] + '/chat_properties')
        chatProperties = json.loads(data.decode('utf-8'))
        
        if db.isChannelBannedReason(msgParts[3]):
            send('Chat ' + msgParts[3] + ' is banned from joining')
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
            send('Auto join for ' + msgParts[3] + ' is now enabled and '
                        'joined ' + msgParts[3] + ' chat')
        elif result:
            if rejoin < 0:
                msg = 'Auto join for ' + msgParts[3]
                msg += ' is now enabled and moved to the correct server'
            else:
                msg = 'Auto join for ' + msgParts[3] + ' is now enabled'
            send(msg)
        elif not wasInChat:
            send('Auto join for ' + msgParts[3] + ' is already enabled '
                        'but now joined ' + msgParts[3] + ' chat')
        else:
            if rejoin < 0:
                msg = 'Auto join for ' + msgParts[3]
                msg += ' is already enabled and moved to the correct server'
            else:
                msg = 'Auto join for ' + msgParts[3]
                msg += ' is already enabled and already in chat'
            send(msg)
        return True
    if msgParts[2] in ['del', 'delete', 'rem', 'remove', 'remove']:
        result = db.discardAutoJoin(msgParts[3])
        if result:
            send('Auto join for ' + msgParts[3] + ' is now '
                        'disabled')
        else:
            send('Auto join for ' + msgParts[3] + ' was never '
                        'enabled')
        return True
    if msgParts[2] in ['pri', 'priority']:
        try:
            priority = int(msgParts[4])
        except:
            priority = 0
        result = db.setAutoJoinPriority(msgParts[3], priority)
        if result:
            send('Auto join for ' + msgParts[3] + ' is set to '
                        'priority ' + str(priority))
        else:
            send('Auto join for ' + msgParts[3] + ' was never '
                        'enabled')
        return True
    return False
