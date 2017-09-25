from lib.data import ChatCommandArgs
from lib.helper.chat import permission, ownerChannel, send
from ..library import broadcaster


@permission('broadcaster')
async def commandHello(args: ChatCommandArgs) -> bool:
    args.chat.send('Hello Kappa !')
    return True


@ownerChannel
async def commandCome(args: ChatCommandArgs) -> bool:
    return await broadcaster.come(args.database, args.nick, send(args.chat))


@permission('broadcaster')
async def commandLeave(args: ChatCommandArgs) -> bool:
    return await broadcaster.leave(args.chat.channel, send(args.chat))


@permission('broadcaster')
async def commandEmpty(args: ChatCommandArgs) -> bool:
    return broadcaster.empty(args.chat.channel, send(args.chat))


@ownerChannel
async def commandAutoJoin(args: ChatCommandArgs) -> bool:
    return await broadcaster.auto_join(args.database, args.nick,
                                       send(args.chat), args.message)


@permission('broadcaster')
async def commandSetTimeoutLevel(args: ChatCommandArgs) -> bool:
    await broadcaster.set_timeout_level(args.database, args.chat.channel,
                                        send(args.chat), args.message)
    return True
