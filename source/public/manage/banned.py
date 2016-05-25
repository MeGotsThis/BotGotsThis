from bot import utils

def manageBanned(database, send, nick, message):
    if len(message) < 3:
        return False
    if message.lower[2] in ['list']:
        bannedChannels = database.listBannedChannels()
        if bannedChannels:
            msg = 'Banned Channels: ' + ', '.join(bannedChannels)
            send(msg)
        else:
            send('There are no banned channels')
        return True
    
    if len(message) < 5:
        if message.lower[2] in ['add', 'insert', 'del', 'delete',
                                'rem', 'remove', 'remove']:
            send(nick + ' -> Reason needs to be specified')
        return False
    channel = message.lower[3]
    if message.lower[2] in ['add', 'insert']:
        isBannedOrReason = database.isChannelBannedReason(channel)
        if isBannedOrReason:
            send(channel + ' is already banned for: ' +
                        isBannedOrReason)
            return False
        params = channel, message[4:], nick
        result = database.addBannedChannel(*params)
        if result:
            database.discardAutoJoin(channel)
            utils.partChannel(channel)
            
        if result:
            send('Chat ' + channel + ' is now banned')
        else:
            send('Chat ' + channel + ' could not be banned. '
                        'Error has occured.')
        return True
    if message.lower[2] in ['del', 'delete', 'rem', 'remove', 'remove']:
        isBannedOrReason = database.isChannelBannedReason(channel)
        if not isBannedOrReason:
            send(channel + ' is not banned')
            return False
        params = channel, message[4:], nick
        result = database.removeBannedChannel(*params)
            
        if result:
            send(channel + ' is now unbanned')
        else:
            send(channel + ' could not be unbanned. Error has occured.')
        return True
    return False
