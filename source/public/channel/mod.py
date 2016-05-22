from ...api import oauth, twitch
import threading

def commandStatus(db, chat, tags, nick, message, tokens, permissions, now):
    if (not permissions.broadcaster and
        db.hasFeature(chat.channel, 'gamestatusbroadcaster')):
        return False
    
    tokens = message.split(None, 1)
    if len(tokens) != 2:
        tokens.append(' ')
    
    if oauth.getOAuthTokenWithDB(db, chat.channel) is None:
        return False
    response, data = twitch.twitchCall(
        chat.channel, 'PUT', '/kraken/channels/' + chat.channel,
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/vnd.twitchtv.v3+json',
            },
        data = {'channel[status]': tokens[1]})
    if response.status == 200:
        chat.sendMessage('Channel Status set as: ' + tokens[1])
    else:
        chat.sendMessage('Channel Status failed to set')
    return True

def commandGame(db, chat, tags, nick, message, tokens, permissions, now):
    if (not permissions.broadcaster and
        db.hasFeature(chat.channel, 'gamestatusbroadcaster')):
        return False
    
    tokens = message.split(None, 1)
    if len(tokens) != 2:
        tokens.append('')
    
    if oauth.getOAuthTokenWithDB(db, chat.channel) is None:
        return False
    if tokens[0].lower() == '!game':
        fullGame = db.getFullGameTitle(tokens[1])
        if fullGame is not None:
            tokens[1] = fullGame
        tokens[1] = tokens[1].replace('Pokemon', 'Pokémon')
        tokens[1] = tokens[1].replace('Pokepark', 'Poképark')
    response, data = twitch.twitchCall(
        chat.channel, 'PUT', '/kraken/channels/' + chat.channel,
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/vnd.twitchtv.v3+json',
            },
        data = {'channel[game]': tokens[1]})
    if response.status == 200:
        if tokens[1]:
            chat.sendMessage('Channel Game set as: ' + tokens[1])
        else:
            chat.sendMessage('Channel Game has been unset')
    else:
        chat.sendMessage('Channel Game failed to set')
    return True

def commandPurge(db, chat, tags, nick, message, tokens, permissions, now):
    if permissions.chatModerator and len(tokens) > 1:
        chat.sendMessage('.timeout ' + tokens[1] + ' 1')
        db.recordTimeout(chat.channel, tokens[1], nick, 'purge', None, 1,
                        message, None)
        return True
    return False
