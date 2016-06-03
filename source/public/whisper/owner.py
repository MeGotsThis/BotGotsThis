from ..library import channel, exit, managebot
from ..library.whisper import min_args, permission, send
from bot import globals, utils

@permission('owner')
def commandHello(args):
    utils.whisper(args.nick, 'Hello Kappa')
    return True

@permission('owner')
def commandExit(args):
    exit.botExit(send(args.nick))
    return True

@permission('owner')
def commandSay(args):
    if args.message.lower[1] in globals.channels:
        channel.botSay(args.database, args.nick, args.message.lower[1],
                       args.message[2:])
    return True

@min_args(2)
def commandJoin(args):
    channel.botJoin(args.database, args.message.lower[1], send(args.nick))
    return True

@min_args(2)
def commandPart(args):
    channel.botPart(args.message.lower[1], send(args.nick))
    return True

@permission('admin')
def commandEmptyAll(args):
    channel.botEmptyAll(send(args.nick))
    return True

@min_args(2)
@permission('admin')
def commandEmpty(args):
    channel.botEmpty(args.message.lower[1], send(args.nick))
    return True

@min_args(2)
@permission('owner')
def commandManageBot(args):
    return managebot.botManageBot(args.database, send(args.nick), args.nick,
                                  args.message)
