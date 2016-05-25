from ...api import twitch
from bot import globals, utils
import datetime
import json

def manageAutoJoin(args):
    if len(args.message) < 3:
        return False
    if args.message.lower[2] in ['reloadserver']:
        for channelRow in args.database.getAutoJoinsChats():
            cluster = twitch.twitchChatServer(channelRow['broadcaster'])
            if channelRow['cluster'] != cluster['eventchat']:
                params = channelRow['broadcaster'], cluster,
                args.database.setAutoJoinServer(*params)
                    
                params = channelRow['broadcaster'], channelRow['priority'],
                params += cluster,
                rejoin = utils.ensureServer(*params)
                
                print('{time} Set Server for {channel}'.format(
                    time=datetime.datetime.utcnow(),
                    channel=channelRow['broadcaster']))
        args.send('Auto Join reload server complete')
        return True
    
    if len(args.message) < 4:
        return False
    if args.message.lower[2] in ['add', 'insert', 'join']:
        if args.database.isChannelBannedReason(args.message.lower[3]):
            args.send('Chat ' + args.message.lower[3]
                      + ' is banned from joining')
            return True
        cluster = twitch.twitchChatServer(args.message.lower[3])
        params = args.message.lower[3], 0, cluster
        result = args.database.saveAutoJoin(*params)
        priority = args.database.getAutoJoinsPriority(args.message.lower[3])
        if result == False:
            args.database.setAutoJoinServer(args.message.lower[3], cluster)
            
        wasInChat = args.message.lower[3] in globals.channels
        if not wasInChat:
            utils.joinChannel(args.message.lower[3], priority, cluster)
        else:
            rejoin = utils.ensureServer(
                args.message.lower[3], priority, cluster)
        
        if result and not wasInChat:
            args.send('Auto join for ' + args.message.lower[3] + ' is now '
                      'enabled and joined ' + args.message.lower[3] + ' chat')
        elif result:
            if rejoin < 0:
                msg = 'Auto join for ' + args.message.lower[3]
                msg += ' is now enabled and moved to the correct server'
            else:
                msg = 'Auto join for ' + args.message.lower[3] + ' is now'
                msg += ' enabled'
            args.send(msg)
        elif not wasInChat:
            args.send('Auto join for ' + args.message.lower[3] + ' is already '
                      'enabled but now joined ' + args.message.lower[3] +
                      ' chat')
        else:
            if rejoin < 0:
                msg = 'Auto join for ' + args.message.lower[3]
                msg += ' is already enabled and moved to the correct server'
            else:
                msg = 'Auto join for ' + args.message.lower[3]
                msg += ' is already enabled and already in chat'
            args.send(msg)
        return True
    if args.message.lower[2] in ['del', 'delete', 'rem', 'remove', 'remove']:
        result = args.database.discardAutoJoin(args.message.lower[3])
        if result:
            args.send('Auto join for ' + args.message.lower[3]
                      + ' is now disabled')
        else:
            args.send('Auto join for ' + args.message.lower[3]
                      + ' was never enabled')
        return True
    if args.message.lower[2] in ['pri', 'priority']:
        try:
            priority = int(args.message[4])
        except:
            priority = 0
        result = args.database.setAutoJoinPriority(
            args.message.lower[3], priority)
        if result:
            args.send('Auto join for ' + args.message.lower[3]
                       + ' is set to priority ' + str(priority))
        else:
            args.send('Auto join for ' + args.message.lower[3]
                      + ' was never enabled')
        return True
    return False
