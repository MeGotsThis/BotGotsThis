from lib.data import ChatCommandArgs
from lib.helper.chat import permission, ownerChannel, send
from . import library


@permission('broadcaster')
async def commandHello(args: ChatCommandArgs) -> bool:
    args.chat.send('Hello Kappa !')
    return True


@ownerChannel
async def commandCome(args: ChatCommandArgs) -> bool:
    return await library.come(args.database, args.nick, send(args.chat))


@permission('broadcaster')
async def commandLeave(args: ChatCommandArgs) -> bool:
    return await library.leave(args.chat.channel, send(args.chat))


@ownerChannel
async def commandAutoJoin(args: ChatCommandArgs) -> bool:
    return await library.auto_join(args.database, args.nick, send(args.chat),
                                   args.message)
