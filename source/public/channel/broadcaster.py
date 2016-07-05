from datetime import datetime, timedelta
from ..library import broadcaster
from ..library.chat import cooldown, permission, ownerChannel, send
from ...api import twitch
from ...data import ChatCommandArgs


@permission('broadcaster')
def commandHello(args: ChatCommandArgs) -> bool:
    args.chat.send('Hello Kappa')
    return True


@ownerChannel
def commandCome(args: ChatCommandArgs) -> bool:
    broadcaster.botCome(args.database, args.nick, send(args.chat))
    return True


@permission('broadcaster')
def commandLeave(args: ChatCommandArgs) -> bool:
    return broadcaster.botLeave(args.chat.channel, send(args.chat))


@permission('broadcaster')
def commandEmpty(args: ChatCommandArgs) -> bool:
    broadcaster.botEmpty(args.chat.channel, send(args.chat))
    return True


@ownerChannel
def commandAutoJoin(args: ChatCommandArgs) -> bool:
    broadcaster.botAutoJoin(args.database, args.nick, send(args.chat),
                            args.message)
    return True


@permission('broacaster')
def commandSetTimeoutLevel(args: ChatCommandArgs) -> bool:
    broadcaster.botSetTimeoutLevel(args.database, args.chat.channel,
                                   send(args.chat), args.message)
    return True


@cooldown(timedelta(seconds=60), 'uptime')
def commandUptime(args: ChatCommandArgs) -> bool:
    if not args.chat.isStreaming:
        args.chat.send(
            '{channel} is currently not streaming or has not been for a '
            'minute'.format(channel=args.chat.channel))
        return True

    currentTime = twitch.server_time()  # type: datetime
    if currentTime:
        uptime = currentTime - args.chat.streamingSince  # type: timedelta
        args.chat.send('Uptime: {uptime}'.format(uptime=uptime))
        return True
    else:
        args.chat.send('Fail to get information from Twitch.tv')
