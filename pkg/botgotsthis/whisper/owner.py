from bot import utils
from source.data import WhisperCommandArgs
from source.helper.whisper import min_args, permission, send
from ..library import channel, exit, managebot


@permission('manager')
async def commandHello(args: WhisperCommandArgs) -> bool:
    utils.whisper(args.nick, 'Hello Kappa !')
    return True


@permission('owner')
async def commandExit(args: WhisperCommandArgs) -> bool:
    return await exit.exit(send(args.nick))


@permission('manager')
async def commandSay(args: WhisperCommandArgs) -> bool:
    return await channel.say(args.nick, args.message.lower[1],
                             args.message[2:])


@min_args(2)
async def commandJoin(args: WhisperCommandArgs) -> bool:
    return await channel.join(args.database, args.message.lower[1],
                              send(args.nick))


@min_args(2)
async def commandPart(args: WhisperCommandArgs) -> bool:
    return channel.part(args.message.lower[1], send(args.nick))


@permission('admin')
async def commandEmptyAll(args: WhisperCommandArgs) -> bool:
    return channel.empty_all(send(args.nick))


@min_args(2)
@permission('admin')
async def commandEmpty(args: WhisperCommandArgs) -> bool:
    return channel.empty(args.message.lower[1], send(args.nick))


@min_args(2)
@permission('manager')
async def commandManageBot(args: WhisperCommandArgs) -> bool:
    return await managebot.manage_bot(args.database, args.permissions,
                                      send(args.nick), args.nick, args.message)
