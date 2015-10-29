from ...api import oauth, twitch
from ...database.factory import getDatabase
import threading

def commandStatus(channelData, nick, message, msgParts, permissions):
    msgParts = message.split(None, 1)
    if len(msgParts) != 2:
        return False
    
    if oauth.getOAuthToken(channelData.channel) is None:
        return False
    chan = channelData.channel[1:]
    response, data = twitch.twitchCall(
        channelData.channel, 'PUT', '/kraken/channels/' + chan,
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/vnd.twitchtv.v3+json',
            },
        data = {'channel[status]': msgParts[1]})
    if response.status == 200:
        channelData.sendMessage('Channel Status set as: ' + msgParts[1])
    else:
        channelData.sendMessage('Channel Status failed to set')
    return True

def commandGame(channelData, nick, message, msgParts, permissions):
    msgParts = message.split(None, 1)
    if len(msgParts) != 2:
        msgParts.append('')
    
    if oauth.getOAuthToken(channelData.channel) is None:
        return False
    if msgParts[0].lower() == '!game':
        with getDatabase() as db:
            fullGame = db.getFullGameTitle(msgParts[1])
            if fullGame is not None:
                msgParts[1] = fullGame
        msgParts[1] = msgParts[1].replace('Pokemon', 'Pokémon')
        msgParts[1] = msgParts[1].replace('Pokepark', 'Poképark')
    chan = channelData.channel[1:]
    response, data = twitch.twitchCall(
        channelData.channel, 'PUT', '/kraken/channels/' + chan,
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/vnd.twitchtv.v3+json',
            },
        data = {'channel[game]': msgParts[1]})
    if response.status == 200:
        if msgParts[1]:
            channelData.sendMessage('Channel Game set as: ' + msgParts[1])
        else:
            channelData.sendMessage('Channel Game has been unset')
    else:
        channelData.sendMessage('Channel Game failed to set')
    return True

def commandPurge(channelData, nick, message, msgParts, permissions):
    if permissions['channelModerator'] and len(msgParts) > 1:
        channelData.sendMessage('.timeout ' + msgParts[1] + ' 1')
        return True
    return False
