from source.data import ChatCommandArgs
from source.helper.chat import min_args, permission, send
from ..library import feature


@permission('broadcaster')
@min_args(2)
async def commandFeature(args: ChatCommandArgs) -> bool:
    return await feature.feature(args.database, args.chat.channel,
                                 args.message, send(args.chat))
