from ..library import feature
from ..library.chat import permission, send


@permission('broadcaster')
def commandFeature(args):
    return feature.botFeature(args.database, args.chat.channel, args.message,
                              send(args.chat))
