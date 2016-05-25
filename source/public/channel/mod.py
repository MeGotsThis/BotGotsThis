from ...api import oauth, twitch
import threading

def commandStatus(args):
    if (not args.permissions.broadcaster and
        args.database.hasFeature(args.chat.channel, 'gamestatusbroadcaster')):
        return False
    
    if oauth.getOAuthTokenWithDB(args.database, args.chat.channel) is None:
        return False
    response, data = twitch.twitchCall(
        args.chat.channel, 'PUT', '/kraken/channels/' + args.chat.channel,
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/vnd.twitchtv.v3+json',
            },
        data = {'channel[status]': args.message.query or ' '})
    if response.status == 200:
        args.chat.sendMessage('Channel Status set as: ' + args.message.query)
    else:
        args.chat.sendMessage('Channel Status failed to set')
    return True

def commandGame(args):
    if (not args.permissions.broadcaster and
        args.database.hasFeature(args.chat.channel, 'gamestatusbroadcaster')):
        return False
    
    if oauth.getOAuthTokenWithDB(args.database, args.chat.channel) is None:
        return False
    gameToSet = args.message.query
    if args.message.command == '!game':
        fullGame = args.database.getFullGameTitle(args.message.lower[1])
        if fullGame is not None:
            gameToSet = fullGame
        gameToSet = gameToSet.replace('Pokemon', 'Pokémon')
        gameToSet = gameToSet.replace('Pokepark', 'Poképark')
    response, data = twitch.twitchCall(
        args.chat.channel, 'PUT', '/kraken/channels/' + args.chat.channel,
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/vnd.twitchtv.v3+json',
            },
        data = {'channel[game]': gameToSet})
    if response.status == 200:
        if gameToSet:
            args.chat.sendMessage('Channel Game set as: ' + gameToSet)
        else:
            args.chat.sendMessage('Channel Game has been unset')
    else:
        args.chat.sendMessage('Channel Game failed to set')
    return True

def commandPurge(args):
    if args.permissions.chatModerator and len(args.message) > 1:
        args.chat.sendMessage('.timeout ' + args.message[1] + ' 1')
        args.database.recordTimeout(
            args.chat.channel, args.message[1], args.nick, 'purge', None, 1,
            args.message, None)
        return True
    return False
