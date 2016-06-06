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
                    time=args.timestamp, channel=channelRow['broadcaster']))
        args.send('Auto Join reload server complete')
        return True
    
    if len(args.message) < 4:
        return False
    if args.message.lower[2] in ['add', 'insert', 'join']:
        if args.database.isChannelBannedReason(args.message.lower[3]):
            args.send('Chat {channel} is banned from joining'.format(
                channel=args.message.lower[3]))
            return True
        cluster = twitch.twitchChatServer(args.message.lower[3])
        params = args.message.lower[3], 0, cluster
        result = args.database.saveAutoJoin(*params)
        priority = args.database.getAutoJoinsPriority(args.message.lower[3])
        if result is False:
            args.database.setAutoJoinServer(args.message.lower[3], cluster)
            
        wasInChat = args.message.lower[3] in globals.channels
        if not wasInChat:
            utils.joinChannel(args.message.lower[3], priority, cluster)
        else:
            rejoin = utils.ensureServer(
                args.message.lower[3], priority, cluster)
        
        if result and not wasInChat:
            msg = ('Auto join for {channel} is now enabled and joined '
                   '{channel} chat')
        elif result:
            if rejoin < 0:
                msg = ('Auto join for {channel} is now enabled and moved to '
                       'the correct server')
            else:
                msg = 'Auto join for {channel} is now enabled'
        elif not wasInChat:
            msg = ('Auto join for {channel} is already enabled but now joined '
                   '{channel} chat')
        else:
            if rejoin < 0:
                msg = ('Auto join for {channel} is already enabled and moved '
                       'to the correct server')
            else:
                msg = ('Auto join for {channel} is already enabled and '
                       'already in chat')
        args.send(msg.format(channel=args.message.lower[3]))
        return True
    if args.message.lower[2] in ['del', 'delete', 'rem', 'remove', 'remove']:
        result = args.database.discardAutoJoin(args.message.lower[3])
        if result:
            msg = 'Auto join for {channel} is now disabled'
        else:
            msg = 'Auto join for {channel} was never enabled'
        args.send(msg.format(channel=args.message.lower[3]))
        return True
    if args.message.lower[2] in ['pri', 'priority']:
        try:
            priority = int(args.message[4])
        except (ValueError, IndexError):
            priority = 0
        result = args.database.setAutoJoinPriority(
            args.message.lower[3], priority)
        if result:
            msg = 'Auto join for {channel} is set to priority {priority}'
        else:
            msg = 'Auto join for {channel} was never enabled'
        args.send(msg.format(channel=args.message.lower[3],
                             priority=priority))
        return True
    return False
