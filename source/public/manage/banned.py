from bot import utils

def manageBanned(db, send, nick, message, msgParts):
    if len(msgParts) < 3:
        return False
    msgParts[2] = msgParts[2].lower()
    if msgParts[2] in ['list']:
        bannedChannels = db.listBannedChannels()
        if bannedChannels:
            msg = 'Banned Channels: ' + ', '.join(bannedChannels)
            send(msg)
        else:
            send('There are no banned channels')
        return True
    
    if len(msgParts) < 5:
        if msgParts[2] in ['add', 'insert', 'del', 'delete',
                           'rem', 'remove', 'remove']:
            send(nick + ' -> Reason needs to be specified')
        return False
    msgParts = message.split(None, 4)
    channel = msgParts[3].lower()
    if msgParts[2] in ['add', 'insert']:
        isBannedOrReason = db.isChannelBannedReason(channel)
        if isBannedOrReason:
            send(channel + ' is already banned for: ' +
                        isBannedOrReason)
            return False
        params = channel, msgParts[4], nick
        result = db.addBannedChannel(*params)
        if result:
            db.discardAutoJoin(channel)
            utils.partChannel(channel)
            
        if result:
            send('Chat ' + channel + ' is now banned')
        else:
            send('Chat ' + channel + ' could not be banned. '
                        'Error has occured.')
        return True
    if msgParts[2] in ['del', 'delete', 'rem', 'remove', 'remove']:
        isBannedOrReason = db.isChannelBannedReason(channel)
        if not isBannedOrReason:
            send(channel + ' is not banned')
            return False
        params = channel, msgParts[4], nick
        result = db.removeBannedChannel(*params)
            
        if result:
            send(channel + ' is now unbanned')
        else:
            send(channel + ' could not be unbanned. Error has occured.')
        return True
    return False
