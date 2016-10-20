from ..library import channel, exit, managebot
from ..library.whisper import min_args, permission, send
from bot import utils
from ...data import WhisperCommandArgs


@permission('manager')
def commandHello(args: WhisperCommandArgs) -> bool:
    utils.whisper(args.nick, 'Hello Kappa !')
    return True


@permission('owner')
def commandExit(args: WhisperCommandArgs) -> bool:
    return exit.exit(send(args.nick))


@permission('manager')
def commandSay(args: WhisperCommandArgs) -> bool:
    return channel.say(args.database, args.nick, args.message.lower[1],
                       args.message[2:])


@min_args(2)
def commandJoin(args: WhisperCommandArgs) -> bool:
    return channel.join(args.database, args.message.lower[1],
                        send(args.nick))


@min_args(2)
def commandPart(args: WhisperCommandArgs) -> bool:
    return channel.part(args.message.lower[1], send(args.nick))


@permission('admin')
def commandEmptyAll(args: WhisperCommandArgs) -> bool:
    return channel.empty_all(send(args.nick))


@min_args(2)
@permission('admin')
def commandEmpty(args: WhisperCommandArgs) -> bool:
    return channel.empty(args.message.lower[1], send(args.nick))


@min_args(2)
@permission('manager')
def commandManageBot(args: WhisperCommandArgs) -> bool:
    return managebot.manage_bot(args.database, args.permissions,
                                send(args.nick), args.nick, args.message)
