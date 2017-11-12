from datetime import timedelta, datetime  # noqa: F401
from typing import List, Optional  # noqa: F401

from lib.api import oauth, twitch
from lib.data import ChatCommandArgs
from lib.helper.chat import cooldown, permission_not_feature


@cooldown(timedelta(seconds=60), 'uptime')
async def commandUptime(args: ChatCommandArgs) -> bool:
    if not args.chat.isStreaming:
        channel: str = args.chat.channel
        args.chat.send(f'''\
{channel} is currently not streaming or has not been for a minute''')
    else:
        currentTime: Optional[datetime]
        currentTime = await twitch.server_time()
        if currentTime is not None:
            uptime: timedelta = currentTime - args.chat.streamingSince
            args.chat.send(f'Uptime: {uptime}')
        else:
            args.chat.send('Failed to get information from twitch.tv')
    return True


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
    game = await args.data.getFullGameTitle(args.message.lower[1:]) or game
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
                    name: str = await args.data.twitch_get_community_name(
                        communityId)
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
