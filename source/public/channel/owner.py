from bot import globals
from ..library import channel, exit, managebot
from ..library.chat import min_args, permission, ownerChannel, send
from ..library.chat import sendPriority
from ...data.argument import ChatCommandArgs


@ownerChannel
@permission('owner')
def commandExit(args: ChatCommandArgs) -> bool:
    exit.botExit(sendPriority(args.chat, 0))
    return True


@min_args(3)
@ownerChannel
@permission('owner')
def commandSay(args: ChatCommandArgs) -> bool:
    if args.message.lower[1] in globals.channels:
        channel.botSay(args.database, args.nick, args.message.lower[1],
                       args.message[2:])
    return True


@min_args(2)
@ownerChannel
@permission('admin')
def commandJoin(args: ChatCommandArgs) -> bool:
    channel.botJoin(args.database, args.message.lower[1], send(args.chat))
    return True


@min_args(2)
@ownerChannel
@permission('admin')
def commandPart(args: ChatCommandArgs) -> bool:
    channel.botPart(args.message.lower[1], send(args.chat))
    return True


@ownerChannel
@permission('admin')
def commandEmptyAll(args: ChatCommandArgs) -> bool:
    channel.botEmptyAll(send(args.chat))
    return True


@min_args(2)
@ownerChannel
@permission('admin')
def commandEmpty(args: ChatCommandArgs) -> bool:
    channel.botEmpty(args.message.lower[1], send(args.chat))
    return True


@min_args(2)
@ownerChannel
@permission('owner')
def commandManageBot(args: ChatCommandArgs) -> bool:
    return managebot.botManageBot(args.database, send(args.chat), args.nick,
                                  args.message)
