from ..library import channel, exit, managebot
from ..library.whisper import min_args, permission, send
from bot import globals, utils
from ...data.argument import WhisperCommandArgs


@permission('owner')
def commandHello(args: WhisperCommandArgs) -> bool:
    utils.whisper(args.nick, 'Hello Kappa')
    return True


@permission('owner')
def commandExit(args: WhisperCommandArgs) -> bool:
    exit.botExit(send(args.nick))
    return True


@permission('owner')
def commandSay(args: WhisperCommandArgs) -> bool:
    if args.message.lower[1] in globals.channels:
        channel.botSay(args.database, args.nick, args.message.lower[1],
                       args.message[2:])
    return True


@min_args(2)
def commandJoin(args: WhisperCommandArgs) -> bool:
    channel.botJoin(args.database, args.message.lower[1], send(args.nick))
    return True


@min_args(2)
def commandPart(args: WhisperCommandArgs) -> bool:
    channel.botPart(args.message.lower[1], send(args.nick))
    return True


@permission('admin')
def commandEmptyAll(args: WhisperCommandArgs) -> bool:
    channel.botEmptyAll(send(args.nick))
    return True


@min_args(2)
@permission('admin')
def commandEmpty(args: WhisperCommandArgs) -> bool:
    channel.botEmpty(args.message.lower[1], send(args.nick))
    return True


@min_args(2)
@permission('owner')
def commandManageBot(args: WhisperCommandArgs) -> bool:
    return managebot.botManageBot(args.database, send(args.nick), args.nick,
                                  args.message)
