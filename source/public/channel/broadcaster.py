from datetime import timedelta
from ..library import broadcaster
from ..library.chat import cooldown, permission, ownerChannel, send
from ...api import twitch


@permission('broadcaster')
def commandHello(args):
    args.chat.send('Hello Kappa')
    return True

@ownerChannel
def commandCome(args):
    broadcaster.botCome(args.database, args.nick, send(args.chat))
    return True

@permission('broadcaster')
def commandLeave(args):
    return broadcaster.botLeave(args.chat.channel, send(args.chat))

@permission('broadcaster')
def commandEmpty(args):
    broadcaster.botEmpty(args.chat.channel, send(args.chat))
    return True

@ownerChannel
def commandAutoJoin(args):
    broadcaster.botAutoJoin(args.database, args.nick, send(args.chat),
                            args.message)
    return True

@permission('broacaster')
def commandSetTimeoutLevel(args):
    broadcaster.botSetTimeoutLevel(args.database, args.chat.channel,
                                   send(args.chat), args.message)
    return True

@cooldown(timedelta(seconds=60), 'uptime')
def commandUptime(args):
    if not args.chat.isStreaming:
        args.chat.send(
            '{channel} is currently not streaming or has not been for a '
            'minute'.format(channel=args.chat.channel))
        return True

    currentTime = twitch.serverTime()
    if currentTime:
        uptime = currentTime - args.chat.streamingSince
        args.chat.send('Uptime: {uptime}'.format(uptime=uptime))
        return True
    else:
        args.chat.send('Fail to get information from Twitch.tv')
