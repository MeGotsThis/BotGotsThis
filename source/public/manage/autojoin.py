from ...api import twitch
from bot import globals, utils
import json

def manageAutoJoin(db, send, nick, message, tokens):
    if len(tokens) < 3:
        return False
    tokens[2] = tokens[2].lower()
    if tokens[2] in ['reloadserver']:
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
    
    if len(tokens) < 4:
        return False
    tokens[3] = tokens[3].lower()
    if tokens[2] in ['add', 'insert', 'join']:
        if db.isChannelBannedReason(tokens[3]):
            send('Chat ' + tokens[3] + ' is banned from joining')
            return True
        cluster = twitch.twitchChatServer(tokens[3])
        params = tokens[3], 0, cluster
        result = db.saveAutoJoin(*params)
        priority = db.getAutoJoinsPriority(tokens[3])
        if result == False:
            db.setAutoJoinServer(tokens[3], cluster)
            
        wasInChat = tokens[3] in globals.channels
        if not wasInChat:
            utils.joinChannel(tokens[3], priority, cluster)
        else:
            rejoin = utils.ensureServer(tokens[3], priority, cluster)
        
        if result and not wasInChat:
            send('Auto join for ' + tokens[3] + ' is now enabled and '
                        'joined ' + tokens[3] + ' chat')
        elif result:
            if rejoin < 0:
                msg = 'Auto join for ' + tokens[3]
                msg += ' is now enabled and moved to the correct server'
            else:
                msg = 'Auto join for ' + tokens[3] + ' is now enabled'
            send(msg)
        elif not wasInChat:
            send('Auto join for ' + tokens[3] + ' is already enabled '
                        'but now joined ' + tokens[3] + ' chat')
        else:
            if rejoin < 0:
                msg = 'Auto join for ' + tokens[3]
                msg += ' is already enabled and moved to the correct server'
            else:
                msg = 'Auto join for ' + tokens[3]
                msg += ' is already enabled and already in chat'
            send(msg)
        return True
    if tokens[2] in ['del', 'delete', 'rem', 'remove', 'remove']:
        result = db.discardAutoJoin(tokens[3])
        if result:
            send('Auto join for ' + tokens[3] + ' is now '
                        'disabled')
        else:
            send('Auto join for ' + tokens[3] + ' was never '
                        'enabled')
        return True
    if tokens[2] in ['pri', 'priority']:
        try:
            priority = int(tokens[4])
        except:
            priority = 0
        result = db.setAutoJoinPriority(tokens[3], priority)
        if result:
            send('Auto join for ' + tokens[3] + ' is set to '
                        'priority ' + str(priority))
        else:
            send('Auto join for ' + tokens[3] + ' was never '
                        'enabled')
        return True
    return False
