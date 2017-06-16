import asyncio

from datetime import datetime, timedelta
from typing import Optional
from ..library import broadcaster
from ..library.chat import cooldown, permission, ownerChannel, send
from ...api import twitch
from ...data import ChatCommandArgs


@permission('broadcaster')
async def commandHello(args: ChatCommandArgs) -> bool:
    args.chat.send('Hello Kappa !')
    return True


@ownerChannel
async def commandCome(args: ChatCommandArgs) -> bool:
    return await broadcaster.come(args.database, args.nick, send(args.chat))


@permission('broadcaster')
async def commandLeave(args: ChatCommandArgs) -> bool:
    return broadcaster.leave(args.chat.channel, send(args.chat))


@permission('broadcaster')
async def commandEmpty(args: ChatCommandArgs) -> bool:
    return broadcaster.empty(args.chat.channel, send(args.chat))


@ownerChannel
async def commandAutoJoin(args: ChatCommandArgs) -> bool:
    return await broadcaster.auto_join(args.database, args.nick,
                                       send(args.chat), args.message)


@permission('broadcaster')
async def commandSetTimeoutLevel(args: ChatCommandArgs) -> bool:
    broadcaster.set_timeout_level(args.database, args.chat.channel,
                                  send(args.chat), args.message)
    return True


@cooldown(timedelta(seconds=60), 'uptime')
async def commandUptime(args: ChatCommandArgs) -> bool:
    if not args.chat.isStreaming:
        args.chat.send(
            '{channel} is currently not streaming or has not been for a '
            'minute'.format(channel=args.chat.channel))
    else:
        loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
        currentTime: Optional[datetime]
        currentTime = await twitch.server_time()
        if currentTime is not None:
            uptime: timedelta = currentTime - args.chat.streamingSince
            args.chat.send('Uptime: {uptime}'.format(uptime=uptime))
        else:
            args.chat.send('Failed to get information from twitch.tv')
    return True
