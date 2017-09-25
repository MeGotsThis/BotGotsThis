from lib.data import ChatCommandArgs
from lib.helper.chat import min_args, permission, send
from . import library


@permission('broadcaster')
@min_args(2)
async def commandFeature(args: ChatCommandArgs) -> bool:
    return await library.feature(args.database, args.chat.channel,
                                 args.message, send(args.chat))
