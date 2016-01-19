from ...api import oauth, twitch
import threading

def commandStatus(db, chat, tags, nick, message, msgParts, permissions, now):
    msgParts = message.split(None, 1)
    if len(msgParts) != 2:
        return False
    
    if oauth.getOAuthTokenWithDB(db, chat.channel) is None:
        return False
    response, data = twitch.twitchCall(
        chat.channel, 'PUT', '/kraken/channels/' + chat.channel,
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/vnd.twitchtv.v3+json',
            },
        data = {'channel[status]': msgParts[1]})
    if response.status == 200:
        chat.sendMessage('Channel Status set as: ' + msgParts[1])
    else:
        chat.sendMessage('Channel Status failed to set')
    return True

def commandGame(db, chat, tags, nick, message, msgParts, permissions, now):
    msgParts = message.split(None, 1)
    if len(msgParts) != 2:
        msgParts.append('')
    
    if oauth.getOAuthTokenWithDB(db, chat.channel) is None:
        return False
    if msgParts[0].lower() == '!game':
        fullGame = db.getFullGameTitle(msgParts[1])
        if fullGame is not None:
            msgParts[1] = fullGame
        msgParts[1] = msgParts[1].replace('Pokemon', 'Pokémon')
        msgParts[1] = msgParts[1].replace('Pokepark', 'Poképark')
    response, data = twitch.twitchCall(
        chat.channel, 'PUT', '/kraken/channels/' + chat.channel,
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/vnd.twitchtv.v3+json',
            },
        data = {'channel[game]': msgParts[1]})
    if response.status == 200:
        if msgParts[1]:
            chat.sendMessage('Channel Game set as: ' + msgParts[1])
        else:
            chat.sendMessage('Channel Game has been unset')
    else:
        chat.sendMessage('Channel Game failed to set')
    return True

def commandPurge(db, chat, tags, nick, message, msgParts, permissions, now):
    if permissions['channelModerator'] and len(msgParts) > 1:
        chat.sendMessage('.timeout ' + msgParts[1] + ' 1')
        db.recordTimeout(chat.channel, nick, None, 'purge', None, 1,
                        message, None)
        return True
    return False
