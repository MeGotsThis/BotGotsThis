from ...api import twitch
from bot import globals, utils
import json

def manageAutoJoin(db, send, nick, message):
    if len(message) < 3:
        return False
    if message.lower[2] in ['reloadserver']:
        for channelRow in db.getAutoJoinsChats():
            cluster = twitch.twitchChatServer(channelRow['broadcaster'])
            if channelRow['cluster'] != cluster['eventchat']:
                params = channelRow['broadcaster'], cluster,
                db.setAutoJoinServer(*params)
                    
                params = channelRow['broadcaster'], channelRow['priority'],
                params += cluster,
                rejoin = utils.ensureServer(*params)
                    
                print(str(datetime.datetime.utcnow()) + ' Set Server for ' +
                      channelRow['broadcaster'])
        send('Auto Join reload server complete')
        return True
    
    if len(message) < 4:
        return False
    if message.lower[2] in ['add', 'insert', 'join']:
        if db.isChannelBannedReason(message.lower[3]):
            send('Chat ' + message.lower[3] + ' is banned from joining')
            return True
        cluster = twitch.twitchChatServer(message.lower[3])
        params = message.lower[3], 0, cluster
        result = db.saveAutoJoin(*params)
        priority = db.getAutoJoinsPriority(message.lower[3])
        if result == False:
            db.setAutoJoinServer(message.lower[3], cluster)
            
        wasInChat = message.lower[3] in globals.channels
        if not wasInChat:
            utils.joinChannel(message.lower[3], priority, cluster)
        else:
            rejoin = utils.ensureServer(message.lower[3], priority, cluster)
        
        if result and not wasInChat:
            send('Auto join for ' + message.lower[3] + ' is now enabled and '
                        'joined ' + message.lower[3] + ' chat')
        elif result:
            if rejoin < 0:
                msg = 'Auto join for ' + message.lower[3]
                msg += ' is now enabled and moved to the correct server'
            else:
                msg = 'Auto join for ' + message.lower[3] + ' is now enabled'
            send(msg)
        elif not wasInChat:
            send('Auto join for ' + message.lower[3] + ' is already enabled '
                        'but now joined ' + message.lower[3] + ' chat')
        else:
            if rejoin < 0:
                msg = 'Auto join for ' + message.lower[3]
                msg += ' is already enabled and moved to the correct server'
            else:
                msg = 'Auto join for ' + message.lower[3]
                msg += ' is already enabled and already in chat'
            send(msg)
        return True
    if message.lower[2] in ['del', 'delete', 'rem', 'remove', 'remove']:
        result = db.discardAutoJoin(message.lower[3])
        if result:
            send('Auto join for ' + message.lower[3] + ' is now '
                        'disabled')
        else:
            send('Auto join for ' + message.lower[3] + ' was never '
                        'enabled')
        return True
    if message.lower[2] in ['pri', 'priority']:
        try:
            priority = int(message[4])
        except:
            priority = 0
        result = db.setAutoJoinPriority(message.lower[3], priority)
        if result:
            send('Auto join for ' + message.lower[3] + ' is set to '
                        'priority ' + str(priority))
        else:
            send('Auto join for ' + message.lower[3] + ' was never '
                        'enabled')
        return True
    return False
