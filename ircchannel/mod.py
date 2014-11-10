from . import modGames
import config.oauth
import ircbot.twitchApi

def commandStatus(channelThread, nick, message, msgParts, permissions):
    msgParts = message.split(None, 1)
    if len(msgParts) != 2:
        return False
    if config.oauth.getOAuthToken(channelThread.channel) is None:
        return False
    chan = channelThread.channel[1:]
    response = ircbot.twitchApi.twitchCall(
        channelThread.channel, 'PUT', '/kraken/channels/' + chan,
        headers = {'Content-Type': 'application/x-www-form-urlencoded'},
        data = {'channel[status]': msgParts[1]})
    if response.status == 200:
        channelThread.sendMessage('Channel Status set as: ' + msgParts[1])
    else:
        channelThread.sendMessage('Channel Status failed to set')
    return True

def commandGame(channelThread, nick, message, msgParts, permissions):
    msgParts = message.split(None, 1)
    if len(msgParts) != 2:
        return False
    if config.oauth.getOAuthToken(channelThread.channel) is None:
        return False
    if msgParts[0].lower() == '!game':
        if msgParts[1] in modGames.games:
            msgParts[1] = modGames.games[msgParts[1]]
        msgParts[1] = msgParts[1].replace('Pokemon', 'Pokémon')
        msgParts[1] = msgParts[1].replace('Pokepark', 'Poképark')
    chan = channelThread.channel[1:]
    response = ircbot.twitchApi.twitchCall(
        channelThread.channel, 'PUT', '/kraken/channels/' + chan,
        headers = {'Content-Type': 'application/x-www-form-urlencoded'},
        data = {'channel[game]': msgParts[1]})
    if response.status == 200:
        channelThread.sendMessage('Channel Game set as: ' + msgParts[1])
    else:
        channelThread.sendMessage('Channel Game failed to set')
    return True

def commandPurge(channelThread, nick, message, msgParts, permissions):
    if permissions['channelModerator'] and len(msgParts) > 1:
        channelThread.sendMessage('.timeout ' + msgParts[1] + ' 1')
        return True
    return False
