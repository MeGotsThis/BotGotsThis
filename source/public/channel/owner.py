from ..library import channel, exit, managebot
from ..library.chat import min_args, permission, ownerChannel, send
from ..library.chat import sendPriority
from ...data import ChatCommandArgs


@ownerChannel
@permission('owner')
def commandExit(args: ChatCommandArgs) -> bool:
    return exit.exit(sendPriority(args.chat, 0))


@min_args(3)
@ownerChannel
@permission('owner')
def commandSay(args: ChatCommandArgs) -> bool:
    return channel.say(args.database, args.nick, args.message.lower[1],
                       args.message[2:])


@min_args(2)
@ownerChannel
@permission('admin')
def commandJoin(args: ChatCommandArgs) -> bool:
    return channel.join(args.database, args.message.lower[1], send(args.chat))


@min_args(2)
@ownerChannel
@permission('admin')
def commandPart(args: ChatCommandArgs) -> bool:
    return channel.part(args.message.lower[1], send(args.chat))


@ownerChannel
@permission('admin')
def commandEmptyAll(args: ChatCommandArgs) -> bool:
    return channel.empty_all(send(args.chat))


@min_args(2)
@ownerChannel
@permission('admin')
def commandEmpty(args: ChatCommandArgs) -> bool:
    return channel.empty(args.message.lower[1], send(args.chat))


@min_args(2)
@ownerChannel
@permission('owner')
def commandManageBot(args: ChatCommandArgs) -> bool:
    return managebot.manage_bot(args.database, send(args.chat), args.nick,
                                args.message)
