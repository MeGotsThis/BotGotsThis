from ..library.chat import min_args, permission_not_feature, permission
from ...api import oauth, twitch
from ...data import ChatCommandArgs


@permission_not_feature(('broadcaster', None),
                        ('moderator', 'gamestatusbroadcaster'))
def commandStatus(args: ChatCommandArgs) -> bool:
    if oauth.token(args.chat.channel, database=args.database) is None:
        return False
    if twitch.update(args.chat.channel, status=args.message.query):
        if args.message.query:
            msg = 'Channel Status set as: ' + args.message.query
        else:
            msg = 'Channel Status has been unset'
    else:
        msg = 'Channel Status failed to set'
    args.chat.send(msg)
    return True


@permission_not_feature(('broadcaster', None),
                        ('moderator', 'gamestatusbroadcaster'))
def commandGame(args: ChatCommandArgs) -> bool:
    if oauth.token(args.chat.channel, database=args.database) is None:
        return False
    game = args.message.query  # type: str
    game = args.database.getFullGameTitle(args.message.lower[1:]) or game
    game = game.replace('Pokemon', 'Pokémon').replace('Pokepark', 'Poképark')
    if twitch.update(args.chat.channel, game=game):
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
def commandRawGame(args: ChatCommandArgs) -> bool:
    if oauth.token(args.chat.channel, database=args.database) is None:
        return False
    if twitch.update(args.chat.channel, game=args.message.query):
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
@min_args(2)
def commandPurge(args: ChatCommandArgs) -> bool:
    reason = args.message[2:]  # type: str
    args.chat.send(
        '.timeout {user} 1 {reason}'.format(
            user=args.message[1], reason=reason))
    args.database.recordTimeout(
        args.chat.channel, args.message.lower[1], args.nick, 'purge', None, 1,
        str(args.message), reason if reason else None)
    return True


@permission('moderator')
@min_args(2)
def commandPermit(args: ChatCommandArgs) -> bool:
    user = args.message.lower[1]  # type: str
    if args.database.isPermittedUser(args.chat.channel, user):
        if args.database.removePermittedUser(args.chat.channel, user):
            args.chat.send(
                '{mod} -> {user} is now unpermitted in {channel}'.format(
                    mod=args.nick, user=user, channel=args.chat.channel))
        else:
            args.chat.send('{mod} -> Error'.format(mod=args.nick))
    else:
        if args.database.addPermittedUser(args.chat.channel, user, args.nick):
            args.chat.send(
                '{mod} -> {user} is now permitted in {channel}'.format(
                    mod=args.nick, user=user, channel=args.chat.channel))
        else:
            args.chat.send('{mod} -> Error'.format(mod=args.nick))
    return True
