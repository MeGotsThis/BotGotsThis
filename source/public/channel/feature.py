from ..library import feature, send
from ..library.chat import permission

@permission('broadcaster')
def commandFeature(args):
    return feature.botFeature(args.database, args.chat.channel, args.message,
                              send.channel(args.chat))
