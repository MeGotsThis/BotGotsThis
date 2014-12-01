import database.factory
import config.oauth
import ircbot.twitchApi

def commandStatus(channelThread, nick, message, msgParts, permissions):
    msgParts = message.split(None, 1)
    if len(msgParts) != 2:
        return False
    if config.oauth.getOAuthToken(channelThread.channel) is None:
        return False
    chan = channelThread.channel[1:]
    response, data = ircbot.twitchApi.twitchCall(
        channelThread.channel, 'PUT', '/kraken/channels/' + chan,
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/vnd.twitchtv.v2+json',
            },
        data = {'channel[status]': msgParts[1]})
    if response.status == 200:
        channelThread.sendMessage('Channel Status set as: ' + msgParts[1])
    else:
        channelThread.sendMessage('Channel Status failed to set')
    return True

def commandGame(channelThread, nick, message, msgParts, permissions):
    msgParts = message.split(None, 1)
    if len(msgParts) != 2:
        msgParts.append('')
    if config.oauth.getOAuthToken(channelThread.channel) is None:
        return False
    if msgParts[0].lower() == '!game':
        with database.factory.getDatabase() as db:
            fullGame = db.getFullGameTitle(msgParts[1])
            if fullGame is not None:
                msgParts[1] = fullGame
        msgParts[1] = msgParts[1].replace('Pokemon', 'Pokémon')
        msgParts[1] = msgParts[1].replace('Pokepark', 'Poképark')
    chan = channelThread.channel[1:]
    response, data = ircbot.twitchApi.twitchCall(
        channelThread.channel, 'PUT', '/kraken/channels/' + chan,
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/vnd.twitchtv.v2+json',
            },
        data = {'channel[game]': msgParts[1]})
    if response.status == 200:
        if msgParts[1]:
            channelThread.sendMessage('Channel Game set as: ' + msgParts[1])
        else:
            channelThread.sendMessage('Channel Game has been unset')
    else:
        channelThread.sendMessage('Channel Game failed to set')
    return True

def commandPurge(channelThread, nick, message, msgParts, permissions):
    if permissions['channelModerator'] and len(msgParts) > 1:
        channelThread.sendMessage('.timeout ' + msgParts[1] + ' 1')
        return True
    return False

def commandReloadMods(channelThread, nick, message, msgParts, permissions):
    channelThread.clearMods()
    channelThread.sendMessage('.mods', 0)
    channelThread.sendMessage('Reloaded mods for ' + channelThread.channel[1:])
    return True
