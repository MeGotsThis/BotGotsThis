from ...api import oauth, twitch
from ..library.chat import permission_not_feature, permission
import threading

@permission_not_feature(('broadcaster', None),
                        ('moderator', 'gamestatusbroadcaster'))
def commandStatus(args):
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
        msg = 'Channel Status set as: ' + args.message.query
    else:
        msg = 'Channel Status failed to set'
    args.chat.send(msg)
    return True

@permission_not_feature(('broadcaster', None),
                        ('moderator', 'gamestatusbroadcaster'))
def commandGame(args):
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
            msg = 'Channel Game set as: ' + gameToSet
        else:
            msg = 'Channel Game has been unset'
    else:
        msg = 'Channel Game failed to set'
    args.chat.send(msg)
    return True

@permission('moderator')
def commandPurge(args):
    if args.permissions.chatModerator and len(args.message) > 1:
        args.chat.send('.timeout ' + args.message[1] + ' 1')
        args.database.recordTimeout(
            args.chat.channel, args.message[1], args.nick, 'purge', None, 1,
            args.message, None)
        return True
    return False
