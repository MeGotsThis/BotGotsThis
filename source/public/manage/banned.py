from bot import utils

needReason = ['add', 'insert', 'del', 'delete', 'rem', 'remove', 'remove']

def manageBanned(args):
    if len(args.message) < 3:
        return False
    if args.message.lower[2] in ['list']:
        bannedChannels = args.database.listBannedChannels()
        if bannedChannels:
            msg = 'Banned Channels: ' + ', '.join(bannedChannels)
        else:
            msg = 'There are no banned channels'
        args.send(msg)
        return True
    
    if len(args.message) < 5:
        if args.message.lower[2] in needReason:
            args.send(args.nick + ' -> Reason needs to be specified')
        return False
    channel = args.message.lower[3]
    if args.message.lower[2] in ['add', 'insert']:
        isBannedOrReason = args.database.isChannelBannedReason(channel)
        if isBannedOrReason:
            args.send('{channel} is already banned for: {reason}'.format(
                channel=channel, reason = isBannedOrReason))
            return False
        params = channel, args.message[4:], args.nick
        result = args.database.addBannedChannel(*params)
        if result:
            args.database.discardAutoJoin(channel)
            utils.partChannel(channel)
            
        if result:
            msg = 'Chat {channel} is now banned'
        else:
            msg = 'Chat {channel} could not be banned. Error has occured.'
        args.send(msg.format(channel=channel))
        return True
    if args.message.lower[2] in ['del', 'delete', 'rem', 'remove', 'remove']:
        isBannedOrReason = args.database.isChannelBannedReason(channel)
        if not isBannedOrReason:
            args.send('{channel} is not banned'.format(channel=channel))
            return False
        params = channel, args.message[4:], args.nick
        result = args.database.removeBannedChannel(*params)
            
        if result:
            msg =  'Chat {channel} is now unbanned'
        else:
            msg = 'Chat {channel} could not be unbanned. Error has occured.'
        args.send(msg.format(channel=channel))
        return True
    return False
