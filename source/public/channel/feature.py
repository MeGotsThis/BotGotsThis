from ..library import feature
from ..library.chat import permission, send
from ...data.argument import ChatCommandArgs


@permission('broadcaster')
def commandFeature(args: ChatCommandArgs) -> bool:
    return feature.botFeature(args.database, args.chat.channel, args.message,
                              send(args.chat))
