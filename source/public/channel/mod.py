from ...api import oauth, twitch
import threading

def commandStatus(db, chat, tags, nick, message, permissions, now):
    if (not permissions.broadcaster and
        db.hasFeature(chat.channel, 'gamestatusbroadcaster')):
        return False
    
    if oauth.getOAuthTokenWithDB(db, chat.channel) is None:
        return False
    response, data = twitch.twitchCall(
        chat.channel, 'PUT', '/kraken/channels/' + chat.channel,
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/vnd.twitchtv.v3+json',
            },
        data = {'channel[status]': message.query or ' '})
    if response.status == 200:
        chat.sendMessage('Channel Status set as: ' + message.query)
    else:
        chat.sendMessage('Channel Status failed to set')
    return True

def commandGame(db, chat, tags, nick, message, permissions, now):
    if (not permissions.broadcaster and
        db.hasFeature(chat.channel, 'gamestatusbroadcaster')):
        return False
    
    if oauth.getOAuthTokenWithDB(db, chat.channel) is None:
        return False
    gameToSet = message.query
    if message.command == '!game':
        fullGame = db.getFullGameTitle(message.lower[1])
        if fullGame is not None:
            gameToSet = fullGame
        gameToSet = gameToSet.replace('Pokemon', 'Pokémon')
        gameToSet = gameToSet.replace('Pokepark', 'Poképark')
    response, data = twitch.twitchCall(
        chat.channel, 'PUT', '/kraken/channels/' + chat.channel,
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/vnd.twitchtv.v3+json',
            },
        data = {'channel[game]': gameToSet})
    if response.status == 200:
        if gameToSet:
            chat.sendMessage('Channel Game set as: ' + gameToSet)
        else:
            chat.sendMessage('Channel Game has been unset')
    else:
        chat.sendMessage('Channel Game failed to set')
    return True

def commandPurge(db, chat, tags, nick, message, permissions, now):
    if permissions.chatModerator and len(message) > 1:
        chat.sendMessage('.timeout ' + message[1] + ' 1')
        db.recordTimeout(chat.channel, message[1], nick, 'purge', None, 1,
                        message, None)
        return True
    return False
