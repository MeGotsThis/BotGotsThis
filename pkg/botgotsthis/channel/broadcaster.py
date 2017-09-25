from lib.data import ChatCommandArgs
from lib.helper.chat import permission, send
from ..library import broadcaster


@permission('broadcaster')
async def commandEmpty(args: ChatCommandArgs) -> bool:
    return broadcaster.empty(args.chat.channel, send(args.chat))


@permission('broadcaster')
async def commandSetTimeoutLevel(args: ChatCommandArgs) -> bool:
    await broadcaster.set_timeout_level(args.database, args.chat.channel,
                                        send(args.chat), args.message)
    return True
