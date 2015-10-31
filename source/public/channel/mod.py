from ...api import oauth, twitch
import threading

def commandStatus(db, channel, nick, message, msgParts, permissions):
    msgParts = message.split(None, 1)
    if len(msgParts) != 2:
        return False
    
    if oauth.getOAuthToken(channel.channel) is None:
        return False
    response, data = twitch.twitchCall(
        channel.channel, 'PUT', '/kraken/channels/' + channel.channel,
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/vnd.twitchtv.v3+json',
            },
        data = {'channel[status]': msgParts[1]})
    if response.status == 200:
        channel.sendMessage('Channel Status set as: ' + msgParts[1])
    else:
        channel.sendMessage('Channel Status failed to set')
    return True

def commandGame(db, channel, nick, message, msgParts, permissions):
    msgParts = message.split(None, 1)
    if len(msgParts) != 2:
        msgParts.append('')
    
    if oauth.getOAuthTokenWithDB(db, channel.channel) is None:
        return False
    if msgParts[0].lower() == '!game':
        fullGame = db.getFullGameTitle(msgParts[1])
        if fullGame is not None:
            msgParts[1] = fullGame
        msgParts[1] = msgParts[1].replace('Pokemon', 'Pokémon')
        msgParts[1] = msgParts[1].replace('Pokepark', 'Poképark')
    response, data = twitch.twitchCall(
        channel.channel, 'PUT', '/kraken/channels/' + channel.channel,
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/vnd.twitchtv.v3+json',
            },
        data = {'channel[game]': msgParts[1]})
    if response.status == 200:
        if msgParts[1]:
            channel.sendMessage('Channel Game set as: ' + msgParts[1])
        else:
            channel.sendMessage('Channel Game has been unset')
    else:
        channel.sendMessage('Channel Game failed to set')
    return True

def commandPurge(db, channel, nick, message, msgParts, permissions):
    if permissions['channelModerator'] and len(msgParts) > 1:
        channel.sendMessage('.timeout ' + msgParts[1] + ' 1')
        return True
    return False
