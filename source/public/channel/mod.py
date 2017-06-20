import bot.globals

from typing import Optional, cast

from ..library.chat import min_args, permission_not_feature, permission
from ...api import oauth, twitch
from ...data import ChatCommandArgs
from ... import database


@permission_not_feature(('broadcaster', None),
                        ('moderator', 'gamestatusbroadcaster'))
async def commandStatus(args: ChatCommandArgs) -> bool:
    token: Optional[str] = await oauth.token(args.chat.channel)
    if token is None:
        return False
    msg: str
    if await twitch.update(args.chat.channel, status=args.message.query):
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
async def commandGame(args: ChatCommandArgs) -> bool:
    token: Optional[str] = await oauth.token(args.chat.channel)
    if token is None:
        return False
    game: str = args.message.query
    game = await args.database.getFullGameTitle(args.message.lower[1:]) or game
    game = game.replace('Pokemon', 'Pokémon').replace('Pokepark', 'Poképark')
    if await twitch.update(args.chat.channel, game=game):
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
async def commandRawGame(args: ChatCommandArgs) -> bool:
    token: Optional[str] = await oauth.token(args.chat.channel)
    if token is None:
        return False
    if await twitch.update(args.chat.channel, game=args.message.query):
        if args.message.query:
            msg = 'Channel Game set as: ' + args.message.query
        else:
            msg = 'Channel Game has been unset'
    else:
        msg = 'Channel Game failed to set'
    args.chat.send(msg)
    return True


@permission_not_feature(('broadcaster', None),
                        ('moderator', 'gamestatusbroadcaster'))
async def commandCommunity(args: ChatCommandArgs) -> bool:
    token: Optional[str] = await oauth.token(args.chat.channel)
    if token is None:
        return False
    community: Optional[str] = None
    if len(args.message) >= 2:
        community = args.message[1]
    result: Optional[bool]
    result = await twitch.set_channel_community(args.chat.channel, community)
    msg: str
    if result is True:
        if community is not None:
            community = community.lower()
            communityId = bot.globals.twitchCommunity[community]
            communityName = bot.globals.twitchCommunityId[communityId]
            msg = 'Channel Community set as: ' + communityName
        else:
            msg = 'Channel Community has been unset'
    elif result is False:
        msg = 'Channel Community failed to set, {} not exist'.format(community)
    else:
        msg = 'Channel Community failed to set'
    args.chat.send(msg)
    return True


@permission('moderator')
@permission('chatModerator')
@min_args(2)
async def commandPurge(args: ChatCommandArgs) -> bool:
    reason: str = args.message[2:]
    args.chat.send(
        '.timeout {user} 1 {reason}'.format(
            user=args.message[1], reason=reason))
    db_: database.Database
    async with await database.get_database(database.Schema.Timeout) as db_:
        db: database.DatabaseTimeout = cast(database.DatabaseTimeout, db_)
        db.recordTimeout(
            args.chat.channel, args.message.lower[1], args.nick, 'purge', None,
            1, str(args.message), reason if reason else None)
    return True


@permission('moderator')
@min_args(2)
async def commandPermit(args: ChatCommandArgs) -> bool:
    user: str = args.message.lower[1]
    permitted: bool
    permitted = await args.database.isPermittedUser(args.chat.channel, user)
    msg: str
    if permitted:
        if args.database.removePermittedUser(args.chat.channel, user,
                                             args.nick):
            msg = '{mod} -> {user} is now unpermitted in {channel}'
        else:
            msg = '{mod} -> Error'
    else:
        successful: bool = await args.database.addPermittedUser(
            args.chat.channel, user, args.nick)
        if successful:
            msg = '{mod} -> {user} is now unpermitted in {channel}'
        else:
            msg = '{mod} -> Error'
    args.chat.send(msg.format(mod=args.nick, user=user,
                              channel=args.chat.channel))
    return True
