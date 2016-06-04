from ...api import oauth, twitch
from ..library.chat import min_args, permission_not_feature, permission
import threading

@permission_not_feature(('broadcaster', None),
                        ('moderator', 'gamestatusbroadcaster'))
def commandStatus(args):
    if oauth.getOAuthTokenWithDB(args.database, args.chat.channel) is None:
        return False
    if twitch.updateChannel(args.chat.channel, status=args.message.query):
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
    game = args.message.query
    game = args.database.getFullGameTitle(args.message.lower[1:]) or game
    game = game.replace('Pokemon', 'Pokémon').replace('Pokepark', 'Poképark')
    if twitch.updateChannel(args.chat.channel, game=game):
        if game:
            msg = 'Channel Game set as: ' + game
        else:
            msg = 'Channel Game has been unset'
    else:
        msg = 'Channel Game failed to set'
    args.chat.send(msg)
    return True

@permission_not_feature(('broadcaster', None),
                        ('moderator', 'gamestatusbroadcaster'))
def commandRawGame(args):
    if oauth.getOAuthTokenWithDB(args.database, args.chat.channel) is None:
        return False
    if twitch.updateChannel(args.chat.channel, game=args.message.query):
        if args.message.query:
            msg = 'Channel Game set as: ' + args.message.query
        else:
            msg = 'Channel Game has been unset'
    else:
        msg = 'Channel Game failed to set'
    args.chat.send(msg)
    return True

@permission('moderator')
@permission('chatModerator')
@min_args(1)
def commandPurge(args):
    args.chat.send('.timeout {user} 1'.format(user=args.message[1]))
    args.database.recordTimeout(args.chat.channel, args.message[1], args.nick,
                                'purge', None, 1, args.message, None)
    return True
