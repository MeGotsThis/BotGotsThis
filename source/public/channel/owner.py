from bot import globals
from ..library import channel, exit, managebot
from ..library.chat import min_args, permission, ownerChannel, send


@ownerChannel
@permission('owner')
def commandExit(args):
    exit.botExit(send(args.chat))
    return True


@min_args(3)
@ownerChannel
@permission('owner')
def commandSay(args):
    if args.message.lower[1] in globals.channels:
        channel.botSay(args.database, args.nick, args.message.lower[1],
                       args.message[2:])
    return True


@min_args(2)
@ownerChannel
@permission('admin')
def commandJoin(args):
    channel.botJoin(args.database, args.message.lower[1], send(args.chat))
    return True


@min_args(2)
@ownerChannel
@permission('admin')
def commandPart(args):
    channel.botPart(args.message.lower[1], send(args.chat))
    return True


@ownerChannel
@permission('admin')
def commandEmptyAll(args):
    channel.botEmptyAll(send(args.chat))
    return True


@min_args(2)
@ownerChannel
@permission('admin')
def commandEmpty(args):
    channel.botEmpty(args.message.lower[1], send(args.chat))
    return True


@min_args(2)
@ownerChannel
@permission('owner')
def commandManageBot(args):
    return managebot.botManageBot(args.database, send(args.chat), args.nick,
                                  args.message)
