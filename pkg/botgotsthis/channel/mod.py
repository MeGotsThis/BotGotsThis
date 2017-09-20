from typing import List, Optional, cast  # noqa: F401

import bot
from source import database
from source.api import oauth, twitch
from source.data import ChatCommandArgs
from source.helper.chat import min_args, permission_not_feature, permission


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
    communities: List[str] = []
    if len(args.message) >= 2:
        communities = args.message[1:4].split()
    result: Optional[List[str]]
    result = await twitch.set_channel_community(args.chat.channel, communities)
    if result is not None:
        if communities:
            if result:
                communityNames: List[str] = []
                communityId: str
                for communityId in result:
                    name: str = bot.globals.twitchCommunityId[communityId]
                    communityNames.append(name)
                args.chat.send('Channel Community set as: '
                               + ', '.join(communityNames))
            else:
                args.chat.send('''\
Communities not set, they may not exist on Twitch''')
        else:
            args.chat.send('Channel Community has been unset')
    else:
        args.chat.send('Channel Community failed to set')
    return True


@permission('moderator')
@permission('chatModerator')
@min_args(2)
async def commandPurge(args: ChatCommandArgs) -> bool:
    user: str = args.message[1]
    reason: str = args.message[2:]
    args.chat.send(f'.timeout {user} 1 {reason}')
    db_: database.Database
    async with database.get_database(database.Schema.Timeout) as db_:
        db: database.DatabaseTimeout = cast(database.DatabaseTimeout, db_)
        await db.recordTimeout(
            args.chat.channel, args.message.lower[1], args.nick, 'purge', None,
            1, str(args.message), reason if reason else None)
    return True


@permission('moderator')
@min_args(2)
async def commandPermit(args: ChatCommandArgs) -> bool:
    mod: str = args.nick
    user: str = args.message.lower[1]
    channel: str = args.chat.channel
    permitted: bool
    permitted = await args.database.isPermittedUser(args.chat.channel, user)
    msg: str
    successful: bool
    if permitted:
        successful = await args.database.removePermittedUser(
            args.chat.channel, user, args.nick)
        if successful:
            msg = f'{mod} -> {user} is now unpermitted in {channel}'
        else:
            msg = f'{mod} -> Error'
    else:
        successful = await args.database.addPermittedUser(
            args.chat.channel, user, args.nick)
        if successful:
            msg = f'{mod} -> {user} is now unpermitted in {channel}'
        else:
            msg = f'{mod} -> Error'
    args.chat.send(msg)
    return True
