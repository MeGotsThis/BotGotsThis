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
    return broadcaster.come(args.database, args.nick, send(args.chat))


@permission('broadcaster')
def commandLeave(args: ChatCommandArgs) -> bool:
    return broadcaster.leave(args.chat.channel, send(args.chat))


@permission('broadcaster')
def commandEmpty(args: ChatCommandArgs) -> bool:
    return broadcaster.empty(args.chat.channel, send(args.chat))


@ownerChannel
def commandAutoJoin(args: ChatCommandArgs) -> bool:
    return broadcaster.auto_join(args.database, args.nick, send(args.chat),
                                 args.message)


@permission('broacaster')
def commandSetTimeoutLevel(args: ChatCommandArgs) -> bool:
    broadcaster.set_timeout_level(args.database, args.chat.channel,
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
